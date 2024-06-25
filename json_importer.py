#!/usr/bin/env python3
import json
from argparse import ArgumentParser
from pathlib import Path

from database import OpenableDBSession
from import_utils import insert_chat_or_do_nothing, insert_messages


def main():
    parser = ArgumentParser()
    parser.add_argument("input", help="input json file")

    args = parser.parse_args()
    input_json = Path(str(args.input))
    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not "supergroup" in data["type"]:
        print("Input json is not a supergroup.")
        raise SystemExit(1)

    group_name = data["name"]
    group_id = data["id"]
    messages = data["messages"]
    group_id = int(group_id) if group_id.startswith("-100") else int("-100" + group_id)
    print(f"Try to import {len(messages)} message(s) from {group_name} ({group_id})...")

    with OpenableDBSession() as session:
        insert_chat_or_do_nothing(session=session, chat_id=group_id, title=group_name)
        success_count, skip_count, fail_count, fail_messages = insert_messages(
            session=session, chat_id=group_id, messages=messages
        )

    fail_text = ""
    for fail_message in fail_messages:
        fail_text += "\n\t\t{}".format(fail_message)

    print(
        f"Result:\n\tSuccess: {success_count} message(s)\n\tFail: {fail_count} message(s)\n\tSkip: {skip_count} message(s)\n\tFailure Messages:{fail_text}"
    )


if __name__ == "__main__":
    main()
