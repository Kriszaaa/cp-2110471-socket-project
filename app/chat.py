from textual import on, events
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import ScrollableContainer, Horizontal
from textual.widgets import Footer, Header, Button, Static, Placeholder, Input, Pretty, Label, RichLog, Switch
from textual.widget import Widget
from textual.color import Color
from textual.containers import Container

from app.common import *
from app.common.client import *


# ! ============================== Left side =============================================
class Left(Static):
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
        # yield JoinGroup()


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
    pressed_chatName = reactive('default is here',always_update=True)

    BINDINGS = [
        ('r','add_chatbox',"Refresh list on group/clients")
    ]
    def __init__(self,agent):
        super().__init__()
        self.agent = agent
        self.all_cli = self.agent.get_groups()[1]
        self.pinned_chat = []


    def compose(self):
        with ScrollableContainer(id='chatList'):
            yield ChatBox(gname="default",chat_type='c',agent=self.agent)

    def action_add_chatbox(self):
        chatboxes = self.query(ChatBox)
        if chatboxes :
            chatboxes.remove()
        container = self.query_one("#chatList")
        chatboxes = []
        pinned_chatboxes = []
        for i,c in enumerate(self.agent.get_groups()[1]):
            gname = "(GROUP) "+c
            chatbox = ChatBox(gname=gname , chat_type='g' , agent=self.agent)
            if gname in self.pinned_chat:
                chatbox.gname = '(Pin'+chatbox.gname[1:]
                pinned_chatboxes.append(chatbox)
            else:
                chatboxes.append(chatbox)
            # container.mount(chatbox)
        for i,c in enumerate(self.agent.get_connected_clients()[1]):
            gname = "(CLIENT) "+c
            chatbox = ChatBox(gname=gname , chat_type='c' , agent=self.agent)
            if gname in self.pinned_chat:
                chatbox.gname = '(Pin'+chatbox.gname[1:]
                pinned_chatboxes.append(chatbox)
            else:
                chatboxes.append(chatbox)
            # container.mount(chatbox) 
        for i in pinned_chatboxes:
            container.mount(i)
        for i in chatboxes:
            container.mount(i)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        button_name = event.button.name
        if button_id == "startChat":
            # button.startChat()
            if button_name.split()[2] == 'g':
                if self.agent.join_group(group_name = button_name.split()[1].strip(' ')) == MessageProtocolResponse.OK:
                    self.pressed_chatName = button_name.split()[1]
                    print('In to chat group',self.pressed_chatName)
            else:
                self.pressed_chatName = button_name.split()[1]
        else:
            button_name = event.button.name
            self.pinned_chat.append(button_name)
            self.action_add_chatbox()


class ChatBox(Static):

    pressed_chatName = reactive('default chat name')

    def __init__(self , gname = 'Default group name' ,chat_type = '',agent = None):
        super().__init__()
        self.gname = gname
        self.chat_type = chat_type
        self.agent = agent

    def compose(self):
        yield Label(self.gname, id='chatBoxName')
        yield Box(self.gname , self.chat_type)
    
    # def on_button_pressed(self, event: Button.Pressed) -> None:
    #     """Event handler called when a button is pressed."""
    #     button_id = event.button.id

    #     button = self.query_one(Box)
    #     if button_id == "startChat":
    #         # button.startChat()
    #         if self.chat_type == 'g':
    #             if self.agent.join_group(group_name = self.gname.split()[1]) == MessageProtocolResponse.OK:
    #                 self.pressed_chatName = self.gname
    #                 print('In to chat group',self.pressed_chatName)
        # elif button_id == 'pinChat':
        # return self.gname

    def get_chatName(self):
        return self.gname

class Box(Static):
    def __init__(self,gname,chat_type):
        super().__init__()
        self.gname = gname
        self.chat_type = chat_type

    def compose(self):
        yield Button(label='chat',name=self.gname+' '+self.chat_type, id='startChat')
        yield Button(label='pin',name=self.gname, id='pinChat')

    # def startChat(self, name: str) -> None:
    #     """Method to start chat."""
    #     self.agent.join_group() == MessageProtocolResponse.OK:
    #         print(f'Chat started in {name}')
        
    # def pinChat(self, name: str) -> None:
    #     """Method to pin chat"""
    #     log(f'Chat pinned in {name}')


class Bottom(Static):
    def compose(self):
        with ScrollableContainer(id='announcementList'):
            yield Announcement()
        yield Broadcast()
    
    @on(Button.Pressed , '#broadCastButton')
    def setAccounce(self):
        container = self.query_one('#announcementList')
        container.mount(Announcement(label=self.query_one(Broadcast).broadcastMessage))

class Announcement(Static):
    def __init__(self,label ='announcement text' ):
        super().__init__()
        self.label = label
        
    def compose(self):
        yield Label('announcement text', id='announcementBox')


class Broadcast(Static):
    def __init__(self):
        super().__init__();
        self.broadcastMessage = ''
    def compose(self):
        yield Input(id='broadCastInput', classes='topInput')
        yield Button('broadcast', id='broadcastButton', classes='topButton')


# !======================================================================================

# ! ============================= Right side =============================================
# chat_name = 'Talk Arai U Dai'

class Right(Static):
    
    def __init__(self):
        super().__init__()


    def compose(self):
        # yield Label('wee')
        yield ChatName()
        with ScrollableContainer(id='chat'):
            yield MessageBox('default')
            
        yield InputText()
        yield Footer()
    
    # def watch_chat_name(self) -> None:
    #     self.query_one(Label,'#chatName').chat_name = self.chat_name


# TODO give Title of chatroom
class ChatName(Static):

    chat_name = 'chat_name'
    def __init__(self):
        super().__init__()

    def compose(self):
        yield Label(self.chat_name, id='chatName')
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
            self.query_one(CreateGroup).groupname = ''
    
    #Annouce broadcast
    @on(Input.Changed , '#broadCastInput')
    def annouceHandler(self,event:Input.Changed) -> None:
        self.query_one(Broadcast).broadcastMessage = event.value
    @on(Button.Pressed , '#broadCastButton')
    def sendAnnouce(self):
        self.agent.announce(data=self.query_one(Broadcast).broadcastMessage)
        self.query_one(Broadcast).broadcastMessage = ''


    def on_mount(self) -> None:
        def update_chatname(new_chatname:str) ->None:
            self.query_one(ChatName).chat_name = new_chatname
        self.watch(self.query_one(Middle) , 'pressed_chatName' , update_chatname)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.agent.stop()


if __name__ == "__main__":
    client_name = input('Input name: ')
    with ChatApp('localhost' , 50000) as app:
        app.run()
