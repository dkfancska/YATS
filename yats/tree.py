# import dataclasses
import os
from typing import Union, List


class ConversationTreeNode:
    def __init__(self, payload: dict):
        # each isolated node has zero depth.
        self.depth = 0 # the length of the path from the root.
        self.height = 0 # defined recursively as 1 + max(height of children)
        self.children = []
        # every isolated node is a root
        self.isRoot = True 
        # every isolated node is a leaf
        self.isLeaf = True 
        self.parent = None
        self.payload = payload

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, payload):
        assert isinstance(payload, dict)
        '''payload object carried by tree nodes.'''
        self._payload = payload

    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, parent):
        '''set parent. since this node has a parent it can't be root'''
        if parent is not None:
            self.isRoot = False
            # update the depth.
            self.depth = 1 + parent.depth 
        self._parent = parent

    def __len__(self):
        return len(self.children)

    def __str__(self):
        payload_byte_size = len(
            str(
                self.payload
            ).encode(
                'utf-8'
            )
        )
        return f'''++---- Node [INFO] ----++
    isLeaf: {self.isLeaf}
    isRoot: {self.isRoot}
    payload: {payload_byte_size}B
    depth: {self.depth}
    height: {self.height}
    numChildren: {len(self)}
++---------------------++'''

    def toXML(self):
        childContent = '\n'.join(child.toXML() for child in self)
        op = f'''
<node isRoot="{self.isRoot}" isLeaf="{self.isLeaf}" height="{self.height}" depth="{self.depth}">
    {self.payload}
    {childContent}
</node>'''
        
        return op.strip().strip("\n")

    def __iter__(self):
        for child in self.children:
            yield child

    def append(self, child):
        '''add child node. since this node has a child it can't be a leaf'''
        self.isLeaf = False 
        child.parent = self
        # update the height.
        self.height = 1 + max(self.height-1, child.height)

        self.children.append(child)


class SnscrapeConversationTreeNode(ConversationTreeNode):
    def __init__(self, payload):
        super(SnscrapeConversationTreeNode, self).__init__(payload)
        self.key = "conversation_id"
        self.value = payload[self.key]
        self.node_key = "id"
        self.link_key = "in_reply_to_tweet_id"

    @property
    def isLeaf(self):
        return int(self("reply_count")) == 0
    
    @isLeaf.setter
    def isLeaf(self, value: bool):
        '''this is to make isLeaf an uneditable/read only attribute.'''
        value

    @property
    def id(self):
        return self(self.node_key)

    def pprint(self, prefix="\t"):
        '''pretty print a tree.'''
        for line in str(self).split("\n"):
            print(prefix, line)

    def printr(self, start="", step="\t", leaf_style="\x1b[33;1m{}\x1b[0m"):
        '''recursively print tree.'''
        if self.isLeaf:
            print(start, leaf_style.format(f'id: {self("id")}'))
        else:
            print(start, "id:", self("id"))
        for child in self:
            child.printr(start+step, step)

    def __call__(self, key: str):
        return self.payload.get(key)

    def __repr__(self):
        return f"{self.id}"

    def tolist(self):
        '''return list of path to root'''
        conversation = self.pathToRoot()[::-1]
        return [utterance("text") for utterance in conversation]

    def pathToRoot(self):
        if not self.isRoot:
            return [self] + self.parent.pathToRoot()
        else:
            return [self]

    def __str__(self):
        payload_byte_size = len(
            str(
                self.payload
            ).encode(
                'utf-8'
            )
        )
        return f'''
++---- Node [INFO] ----++
    id: {self("id")}
    conversation_id: {self("id")}
    isLeaf: {self.isLeaf}
    isRoot: {self.isRoot}
    depth: {self.depth}
    height: {self.height}
    numChildren: {len(self)}
++---------------------++
'''


def buildTree(data):
    nodes = {}
    # build dict of nodes.
    for item in data:
        id = item["id"]
        nodes[id] = SnscrapeConversationTreeNode(item)
    # build the tree.
    ctr = 0
    for id, node in nodes.items():
        ctr += 1
        parent_id = node(node.link_key)
        # print(ctr, parent_id)
        if parent_id:
            parent = nodes[parent_id] 
            parent.append(node)

    return nodes

def printTree(node, prefix=""):
    node.pprint(prefix)
    if node.isLeaf:
        return
    print("\x1b[34;1m" + "#"*25 + f" parent:{node.id} " + "#"*25 + "\x1b[0m")
    for child in node:
        printTree(child, prefix+"\t")


if __name__ == "__main__":
    import json
    
    DIR = os.path.dirname(os.path.realpath(__file__))
    PATH = os.path.join(DIR, "../PyQt5_30_convo.json")

    with open(PATH) as f:
        data = json.load(f)
        max_nodes_convo_id = max(data.items(), key=lambda x: len(x[1]))[0]
        print("id of longest conversation:", max_nodes_convo_id)
        largest_conversation = data[max_nodes_convo_id]
        print("largest conversation tree has", len(largest_conversation), "nodes")

    conversation_id = largest_conversation[0]["conversation_id"]
    nodes = buildTree(largest_conversation)
    root = nodes[conversation_id]
    # printTree(root)
    root.printr(start="∟", step="—"*4)
    # path to root.
    for node in nodes.values():
        print(node.pathToRoot()) # last element is the root.
    
    # list format (return list of conversation text till now).
    # for node in nodes.values():
    #     print(node.tolist())
    
    # list all coversations.
    for node in nodes.values():
        if node.isLeaf:
            print(node.tolist())
    