import json
import socket
from database import OpenableDBSession
from import_utils import insert_chat_or_do_nothing, insert_messages
from utils import get_text_func

TEMP_FILE_NAME = "history_temp.json"
BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"

_ = get_text_func()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5006))
    server.listen(3)
    while True:
        print("listening......")
        sock, adddr = server.accept()
        print(_("{}connected").format(adddr))
        received = sock.recv(BUFFER_SIZE).decode()
        try:
            filename, filesize = received.split(SEPARATOR)
        except ValueError:
            sock.close()
            continue
        filesize = int(filesize)
        receivedsize = 0
        with open(TEMP_FILE_NAME, "wb") as f:
            while True:
                bytes_read = sock.recv(BUFFER_SIZE)
                f.write(bytes_read)
                receivedsize += BUFFER_SIZE
                if not bytes_read:
                    break
                if receivedsize >= filesize:
                    print(
                        _("file receive finished {} {}MB\n").format(
                            filename, round(filesize / 1024 / 1024, 2)
                        )
                    )
                    break

        with open(TEMP_FILE_NAME) as f:
            try:
                data = json.load(f)

                group_name = data["name"]
                group_id = data["id"]
                messages = data["messages"]
                group_id = (
                    int(group_id)
                    if group_id.startswith("-100")
                    else int("-100" + group_id)
                )
                supergroup_flag = "supergroup" in data["type"]
            except (json.JSONDecodeError, AttributeError) as e:
                sock.send(_("JSON read error!\n").encode())
                sock.send(str(e).encode())
                sock.close()
                continue

        sock.send(_("checking group info...\n").encode())
        if not supergroup_flag:
            sock.send(_("Not supergroup! stopped!\n").encode())
            sock.close()
            continue

        sock.send(_("importing...").encode())

        print(group_id)
        with OpenableDBSession() as session:
            insert_chat_or_do_nothing(session, group_id, group_name)
            success_count, fail_count, fail_messages = insert_messages(
                session, group_id, messages
            )

        fail_text = ""
        for fail_message in fail_messages:
            fail_text += "{}\n\t".format(fail_message)
        result_text = _(
            "\nresult\n\tgroup: {} ({})\n\tsuccess: {}\n\tfail: {}\n\t{}"
        ).format(group_name, group_id, success_count, fail_count, fail_text)
        sock.sendall(result_text.encode())

        sock.send(_("\nCtrl+C to exit").encode())


if __name__ == "__main__":
    main()
