import os
import shutil
from datetime import datetime, date
import logging
import asyncio

from config import Config
from excel.files import parse_inquiry, parse_main


logging.basicConfig(
    filename=Config.LOG_FILE, format="%(asctime)s - %(message)s", level=logging.INFO
)


"""
main is an async function that runs the main robot logic.

It checks if the main and info files were modified today. 
If so, it archives them, logs the copy, and parses them by 
calling parse_main and parse_inquiry async tasks.

If the files were not changed, it just logs that info.

Finally it logs how long the script took to run.
"""
async def main():
    now = datetime.now()

    main_file_date = date.fromtimestamp(os.path.getmtime(Config.MAIN_FILE))
    info_file_date = date.fromtimestamp(os.path.getmtime(Config.INFO_FILE))

    if date.today() in [main_file_date, info_file_date]:
        for file in [Config.MAIN_FILE, Config.INFO_FILE, Config.DATABASE_URI]:
            try:
                shutil.copy(file, Config.ARCHIVE_DIR)
                logging.info(f"{file} copied to {Config.ARCHIVE_DIR}")
            except Exception as e:
                logging.error(e)

        tasks = [
            parse_main(Config.MAIN_FILE),
            parse_inquiry(Config.INFO_FILE),
        ]
        await asyncio.gather(*tasks)

    else:
        logging.info("Files not changed")

    logging.info(f"Script execution time: {datetime.now() - now}")


if __name__ == "__main__":
    asyncio.run(main())
