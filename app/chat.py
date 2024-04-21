from textual import on, events
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import ScrollableContainer, Horizontal
from textual.widgets import Footer, Header, Button, Static, Placeholder, Input, Pretty, Label, RichLog, Switch
from textual.color import Color
from textual.containers import Container

from app.common import *
from app.common.client import *


# ! ============================== Left side =============================================
class Left(Static):
    BINDINGS = [
        ('r','add_chatbox',"Refresh list on group/clients")
    ]
    def __init__(self,agent):
        super().__init__()
        self.agent = agent

    def compose(self):
        yield Top()
        yield Middle(self.agent)
        yield Bottom()
        yield Footer()


class Top(Static):
    def compose(self):
        yield CreateGroup()
        yield JoinGroup()


class CreateGroup(Static):
    groupname = reactive("")
    def compose(self):
        yield Input(id='createGroupInput', classes='topInput')
        yield Button('create group', id='createGroupButton', classes='topButton')
    



class JoinGroup(Static):
    groupname = reactive("")
    def compose(self):
        yield Input(id='joinGroupInput', classes='topInput')
        yield Button('join group', id='joinGroupButton', classes='topButton')


class Middle(Static):
    BINDINGS = [
        ('r','add_chatbox',"Refresh list on group/clients")
    ]
    def __init__(self,agent):
        super().__init__()
        self.agent = agent
        self.all_cli = self.agent.get_groups()[1]

    def compose(self):
        with ScrollableContainer(id='chatList'):
            yield ChatBox(gname="default")

    def action_add_chatbox(self):
        chatboxes = self.query(ChatBox)
        if chatboxes :
            chatboxes.remove()
        container = self.query_one("#chatList")
        for i,c in enumerate(self.agent.get_groups()[1]):
            chatbox = ChatBox(gname=c)
            container.mount(chatbox)

class ChatBox(Static):
    def __init__(self , gname):
        super().__init__()
        self.gname = gname

    def compose(self):
        yield Label(self.gname, id='chatBoxName')
        yield Box()


class Box(Static):
    def compose(self):
        yield Button('chat', id='startChat')
        yield Button('pin', id='pinChat')


class Bottom(Static):
    def compose(self):
        with ScrollableContainer(id='announcementList'):
            yield Announcement()
            yield Announcement()
            yield Announcement()
            yield Announcement()
            yield Announcement()
            yield Announcement()
            yield Announcement()
        yield Broadcast()


class Announcement(Static):
    def compose(self):
        yield Label('announcement text', id='announcementBox')


class Broadcast(Static):
    def compose(self):
        yield Input(id='broadCastInput', classes='topInput')
        yield Button('broadcast', id='broadcastButton', classes='topButton')


# !======================================================================================

# ! ============================= Right side =============================================
chat_name = 'Talk Arai U Dai'


class Right(Static):
    def compose(self) -> ComposeResult:
        # yield Label('wee')
        yield ChatName()
        with ScrollableContainer(id='chat'):
            yield MessageBox('hi')
            yield MessageBox('wow')
        yield InputText()
        yield Footer()


# TODO give Title of chatroom
class ChatName(Static):
    def compose(self):
        yield Label(chat_name, id='chatName')
        yield Button('switch', id='switch')
        # * switch mode (dark-light)


class MessageBox(Static):
    def __init__(self, param, **kwargs):
        super().__init__(**kwargs)
        self.param = param

    def compose(self):
        yield Label('name')
        yield Label(self.param, classes='message')


class SwitchMode(Static):
    def compose(self):
        yield Button('switch', id='switch')
        # yield Horizontal(
        #     Static("off:     ", classes="label"),
        #     Switch(animate=False),
        #     classes="container",
        # )


# * Input message and send Button div
# TODO apply send message function
class InputText(Static):
    def compose(self):
        yield Input(placeholder='text something...', id='textBox')
        yield Button('send', variant='primary', id='sendButton')
        yield Button('send file', variant='primary', id='sendFileButton')


# !================================================================================


# ! ============================ Control center ==========================================
class ChatApp(App):
    CSS_PATH = 'chat.tcss'
    def __init__(self, remote_host: str, remote_port: int):
        super().__init__()
        self.agent = ChatAgent(client_name,
                               (remote_host, remote_port),
                               4,
                               recv_callback=self.on_receive)
        self.mes = 'asfasf'
        self.groupName = ''

    def on_receive(self, message: MessageProtocol):
        pass

    def compose(self):
        yield Header()
        yield Footer()
        yield Left(self.agent)
        yield Right()

    @on(Button.Pressed, '#switch')
    def switch(self):
        self.agent.send_private('vt', 'safgsfgdjshf')
        self.dark = not self.dark

    @on(Button.Pressed, '#sendButton')
    def action_add_message(self) -> None:
        self.mes = 'how'
        new_message = MessageBox(self.mes)
        self.query_one("#chat").mount(new_message)
        new_message.scroll_visible()

    #create Group
    @on(Input.Changed , '#createGroupInput')
    def groupNameHandler(self,event:Input.Changed) -> None:
        self.query_one(CreateGroup).groupname = event.value
    @on(Button.Pressed , '#createGroupButton')
    def createGroup(self):
        if self.agent.create_group(group_name=self.query_one(CreateGroup).groupname) == MessageProtocolResponse.OK :
            print("GroupName",self.query_one(CreateGroup).groupname)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.agent.stop()


if __name__ == "__main__":
    client_name = input('Input name: ')
    with ChatApp('localhost' , 50000) as app:
        app.run()
