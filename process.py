import asyncio
import os

from viam.logging import getLogger
from viam.robot.client import RobotClient
from viam.services.vision import VisionClient
from viam.components.generic import Generic

LOGGER = getLogger(__name__)

robot_api_key = os.getenv('ROBOT_API_KEY') or ''
robot_api_key_id = os.getenv('ROBOT_API_KEY_ID') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''

# Define the component and service names from the Viam app CONFIGURE tab
vision_name = os.getenv('VISION_NAME') or ''
camera_name = os.getenv('CAMERA_NAME') or ''
piezo_name = os.getenv('PIEZO_NAME') or ''

async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key=robot_api_key,
      api_key_id=robot_api_key_id
    )
    return await RobotClient.at_address(robot_address, opts)

async def main():
    machine = await connect()

    detector = VisionClient.from_robot(machine, vision_name)
    piezo = Generic.from_robot(machine, piezo_name)

    N = 100
    for i in range(N):
        try:
            LOGGER.info(f"Iteration {i+1}/{N}")
            detections = await detector.get_detections_from_camera(camera_name)
            LOGGER.info(f"Raw Detections: {detections}")
            found = False
            for d in detections:
                LOGGER.info(f"Detection: class_name={d.class_name}, confidence={d.confidence}")
                if d.confidence > 0.8 and d.class_name.lower() == "person":
                    LOGGER.info("Person detected! Activating buzzer.")
                    found = True
                    break

            if found:
                await piezo.do_command({
                    "sound_buzzer": {
                        "frequency": 1200,
                        "duration": 1.5,
                        "duty_cycle": 0.7
                    }
                })
            else:
                LOGGER.info("No person detected.")

        except Exception as e:
            LOGGER.error(f"Error during loop iteration: {e}")

        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())