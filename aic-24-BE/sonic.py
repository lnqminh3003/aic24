import asyncio
import os
import json

from asonic import Client
from asonic.enums import Channel
from tqdm import tqdm

import utils

asr_folder = "./data_processing/raw/transcript/"


async def setup():
    c = Client(
        host="127.0.0.1",
        port=1491,
        password="admin",
        max_connections=1000,
    )
    await c.channel(Channel.INGEST)

    files = []
    for file in os.listdir(asr_folder):
        if file.endswith(".json"):
            files.append(file)
    for file in tqdm(files):
        file_path = os.path.join(asr_folder, file)
        print(f'Processing {file_path}')
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)["segments"]
            
            for segment in data:
                frame_list_str = utils.asc_list_compress(
                    list(map(int, segment["frame_list"]))
                )
                
                objData = [
                    str(file.split(".")[0]), 
                    str(segment["start"]), 
                    str(segment["fps"]), 
                    str(segment["prefix"]),
                    frame_list_str
                ]
                delim = "\t"
                assert all([delim not in s for s in objData])
                obj = delim.join(objData)

                obj = utils.unicode_string_compress(obj)
                assert len(obj) <= 128, f"obj {len(obj)}: {obj}, {objData}"

                try:
                    await c.push(
                        collection="asr",
                        bucket="test",
                        obj=obj,
                        text=segment["text"],
                    )
                except Exception as e:
                    print(e)
                    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
