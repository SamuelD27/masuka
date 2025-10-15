from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.utils.progress import progress_manager
import asyncio
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/stream/{session_id}")
async def stream_progress(session_id: str):
    """
    Stream real-time training progress using Server-Sent Events (SSE).

    Connect with EventSource on frontend:
    const eventSource = new EventSource(`/api/progress/stream/${sessionId}`)
    """

    async def event_generator():
        """Generate SSE events."""
        try:
            last_data = None

            while True:
                # Get current progress from Redis
                progress_data = progress_manager.get_progress(session_id)

                if progress_data:
                    # Only send if data changed
                    if progress_data != last_data:
                        last_data = progress_data
                        yield f"data: {json.dumps(progress_data)}\n\n"

                    # Check if training completed or failed
                    if progress_data.get('status') in ['completed', 'failed', 'cancelled']:
                        logger.info(f"Training {session_id} finished with status: {progress_data.get('status')}")
                        break
                else:
                    # Send heartbeat
                    yield f": heartbeat\n\n"

                # Wait before next update
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info(f"SSE connection cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"SSE error for session {session_id}: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
