import functools
import os
import socket
import time

from app.common import *
from app.common.client import *
import sys


def suppress(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class ProgramQuitException(Exception):
    pass


class AppCLI:
    def __init__(self,
                 agent: ChatAgent,
                 app_name: str = 'Chat App (CLI)'):
        self.__agent = agent
        self.__src: tuple[str | None, str | None] = (None, None)
        self.__parser = ProgramArgumentParser(app_name=app_name)
        self.__prev_cmd = ''
        self.__setup_parser()

    def __setup_parser(self):
        self.__parser.add_commands(
            ProgramCommand(
                'list', 'List query',
                ProgramCommandArgument(
                    name='option',
                    help_str='What to list?',
                    data_type=str,
                    choices=['clients', 'groups', 'members'],
                    optional=True
                ), callback=self.__cmd_list,
                aliases=['ls']
            ),
            ProgramCommand(
                'chat', 'Private message with someone',
                ProgramCommandArgument(
                    name='recipient',
                    help_str='Recipient',
                    data_type=str,
                    long_string=True
                ), callback=self.__cmd_chat,
                aliases=['pm']
            ),
            ProgramCommand(
                'create', 'Create a new group (chatroom)',
                ProgramCommandArgument(
                    name='name',
                    help_str='Group name',
                    data_type=str,
                    long_string=True
                ), callback=self.__cmd_group_create,
                aliases=['new']
            ),
            ProgramCommand(
                'join', 'Join a group (chatroom)',
                ProgramCommandArgument(
                    name='name',
                    help_str='Group name',
                    data_type=str,
                    long_string=True
                ), callback=self.__cmd_group_join,
                aliases=['jam']
            ),
            ProgramCommand(
                'leave', 'Leave the group (chatroom)',
                ProgramCommandArgument(
                    name='option',
                    help_str='Leave or leave all',
                    data_type=str,
                    choices=['all'],
                    optional=True
                ),
                callback=self.__cmd_group_leave,
                aliases=['bye']
            ),
            ProgramCommand(
                'send', 'Send message to the recipient/group',
                ProgramCommandArgument(
                    name='message',
                    help_str='Message to send',
                    data_type=str,
                    long_string=True
                ),
                callback=self.__cmd_send_text,
                aliases=['message', 'msg', 'm']
            ),
            ProgramCommand(
                'file', 'Send file to the recipient/group',
                ProgramCommandArgument(
                    name='path',
                    help_str='File path to send',
                    data_type=str,
                    long_string=True
                ),
                callback=self.__cmd_send_file,
                aliases=['send-file', 'f']
            ),
            ProgramCommand(
                'quit', 'Exit the application',
                callback=self.__cmd_quit,
                aliases=['exit', 'q']
            )
        )

    def run(self):
        while True:
            time.sleep(0.25)
            if self.__src[0]:
                prompt_str = self.__construct_sys_prompt(f'{self.__agent.username} [Group: {self.__src[0]}]')
            elif self.__src[1]:
                prompt_str = self.__construct_sys_prompt(f'{self.__agent.username} [To: {self.__src[1]}]')
            else:
                prompt_str = self.__construct_sys_prompt(f'{self.__agent.username}')

            try:
                cmd_input = input(prompt_str).split()
            except KeyboardInterrupt:
                break

            if cmd_input == '!!':
                cmd_input = self.__prev_cmd
            self.__prev_cmd = cmd_input

            try:
                if not self.__parser.execute(cmd_input):
                    print("No command provided. Type 'quit' to exit.")
            except ProgramQuitException:
                break
            except SystemExit:
                continue

    @suppress
    def __cmd_list(self, args):
        if not args.option or args.option == 'clients':
            res = self.__agent.get_connected_clients()[1]
            if res:
                print('Connected clients')
                for i, c in enumerate(res):
                    print(f'[{i:4d}] {c}')
            else:
                print('No client is connected!')
        elif args.option == 'groups':
            res = self.__agent.get_groups()[1]
            if res:
                print('Available groups')
                for i, c in enumerate(res):
                    print(f'[{i:4d}] {c}')
            else:
                print('No group in the server yet!')
        elif args.option == 'members':
            res = self.__agent.get_clients_in_group(self.__src[0])[1]
            if res:
                print(f'Members in group \"{self.__src[0]}\"')
                for i, c in enumerate(res):
                    print(f'[{i:4d}] {c}')
            else:
                print('No client is in the group!')
        return 0

    @suppress
    def __cmd_chat(self, args):
        recipient = ' '.join(args.recipient)
        self.__src = (None, recipient)
        return 0

    @suppress
    def __cmd_group_create(self, args):
        name = ' '.join(args.name)
        if self.__agent.create_group(name) == MessageProtocolResponse.OK:
            print(f'Created group {name}!')
            return 0
        else:
            print(f'Unable to create the group')
            return 1

    @suppress
    def __cmd_group_join(self, args):
        name = ' '.join(args.name)
        if self.__agent.join_group(group_name=name) == MessageProtocolResponse.OK:
            self.__src = (name, None)
            print(f'Joined group: {self.__src[0]}')
            return 0
        else:
            print(f'Error joining group: {self.__src[0]} (Doesn\'t exist)')
            return 1

    @suppress
    def __cmd_group_leave(self, args):
        if args.option:
            self.__agent.leave_group(self.__src[0])
        else:
            self.__agent.leave_all_groups()

        self.__src = (None, self.__src[1])
        return 0

    @suppress
    def __cmd_send_text(self, args):
        message = ' '.join(args.message)
        if self.__src[0]:
            self.__agent.send_group(group_name=self.__src[0],
                                    data_type=MessageProtocolCode.DATA.PLAIN_TEXT,
                                    data=message)
        else:
            self.__agent.send_private(recipient=self.__src[1],
                                      data_type=MessageProtocolCode.DATA.PLAIN_TEXT,
                                      data=message)
        return 0

    @suppress
    def __cmd_send_file(self, args):
        file_path: str = ' '.join(args.path)
        if os.path.isfile(file_path):
            with open(file_path, mode='rb') as f:
                file_content: bytes = f.read()
                file_proto = new_file_proto(filename=os.path.basename(file_path),
                                            content=file_content)
                if self.__src[0]:
                    self.__agent.send_group(group_name=self.__src[0],
                                            data_type=MessageProtocolCode.DATA.FILE,
                                            data=file_proto)
                else:
                    self.__agent.send_private(recipient=self.__src[1],
                                              data_type=MessageProtocolCode.DATA.FILE,
                                              data=file_proto)
            return 0
        else:
            logger.error(f'File {file_path} doesn\'t exist!')
            return 1

    @suppress
    def __cmd_quit(self, _):
        raise ProgramQuitException

    @staticmethod
    def __construct_sys_prompt(s: str):
        return f'[{datetime_fmt()}] {s} > '

    @staticmethod
    def on_receive(message: MessageProtocol):
        if not isinstance(message, MessageProtocol) or not message.src:
            return

        if message.message_type == MessageProtocolCode.DATA.FILE:
            # Receive file
            _file_proto: FileProtocol = message.body
            print(f'[{datetime_fmt()}] {message.src.username}: '
                  f'Sent a file: {_file_proto.filename} '
                  f'(size: {_file_proto.size} bytes)')

            # Save file
            home_dir = os.path.expanduser("~").replace('\\', '/')
            filename = uniquify(f'{home_dir}/Downloads/socket/{_file_proto.filename}')
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, mode='wb') as f:
                f.write(_file_proto.content)

            logger.info(f'File {_file_proto.filename} is saved as \"{filename}\".')

        else:
            # Other format
            print(f'[{datetime_fmt()}] {message.src.username}: {message.body}')


if __name__ == "__main__":
    try:
        client_name = input('Client name > ').strip()
    except KeyboardInterrupt:
        sys.exit(0)

    time.sleep(0.5)
    with ChatAgent(client_name=client_name,
                   open_sockets=128,
                   recv_callback=AppCLI.on_receive,
                   disc_callback=None) as agent:
        app = AppCLI(app_name='app', agent=agent)
        try:
            app.run()
        except socket.socket:
            pass
        except KeyboardInterrupt:
            pass

    logger.info('Bye!')
