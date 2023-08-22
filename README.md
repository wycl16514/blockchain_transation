在区块链的目最重要的目的就是实现价值的转移。这本质上是信息的发布和存储。例如我要正面我有一百块钱，那么我需要拿出一张 100 块的钞票，这张纸币只不过是一种“我有一百块”这个信息的证明。现在我们都有电子支付，于是“我有一百块”这个信息就变成了微信钱包或支付宝余额宝里面的一个数字，你拿给别人看，他人看到数字就相信你有这个价值。

那么交易的本质实质上就是信息的变化。你从一百块中拿出 50 吃了顿饭。那么这个信息就变成“你当前拥有 50 块，饭店老板增加了 50 块”，只要这个信息能被所有人确认，那么我们根本用不着拿出纸币或电子钱包里面的数字来证明。区块链的“交易”就是记录这个信息变化，然后让所有参与者都能准确的获得这个信息。

在区块链的“交易”概念中包含 4 个部分，分别为版本，输入，输出和锁定时间。“版本”用来记录交易的功能范围，想想 windows3.1 和 windows11 这两个系统版本所提供功能的差异，版本号越大意味着功能越强大。输入指的是消耗的比特币数量，输出指的是花掉的比特币给了谁，也就是被花掉比特币的接受者，锁定时间指的是交易何时能生效。下面我们用代码来实现交易这个概念：

import hashlib

def hash256(s):
    # 连续进行两次sha256运算
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

class Tx:
    def __init__(self, version, tx_ins, tx_outs, locktime, testnet=False):
        """
        输入和输出的数据格式在后面会详细定义
        """
        self.version = version
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs
        self.locktime = locktime
        self.testnet = testnet

    def __repr__(self):
        tx_ins = ''
        for tx_in in self.tx_ins:
            tx_ins += tx_in.__repr__() + '\n'

        tx_outs = ''
        for tx_out in self.tx_outs:
            tx_outs += tx_out.__repr__() + '\n'

        return f"tx: {self.id()}\n{self.version}\n: tx_ins:{tx_ins}\n tx_outs:{tx_outs}\n locktime:{self.locktime}\n"

    def id(self):
        # 每个交易都有专门的 id，这样才能进行查询
        return self.hash().hex()

    def hash(self):
        return hash256(self.serialize())[::-1]


    def serialize(self):
        # 以后再具体实现类的序列化
        return f"Tx:{self.version}"

    @classmethod
    def parse(cls,  stream):
        # 将序列化数据转为类实例,以后再实现
        return None
下面我们给出一段区块链交易对应的二进制数据，我将使用{}把要解析的字段标注出来，如果字段还分子字段，那么我会使用[]标注出来，我们先看数据：

'{01000000}01813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d10000000\
06b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02\
207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631\
e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef0100000000\
1976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc\
762dd5423e332166702cb75f40df79fea1288ac19430600
在上面数据中，{}标出来的部分就是交易中有关版本号的字段。它占 4 个字节，以小端编码的方式存储，因此我们解析时需要将其倒转过来变成00000001,由此我们修改上面代码来解读交易数据的版本号如下：

 @classmethod
    def little_endian_to_int(cls, b):
        # 读入数据流读入 4 字节，将其以小端方式存储，然后解读成一个整形 int 数值
        return int.from_bytes(b, 'little')

    @classmethod
    def parse(cls, s):
        #数据流的前 4 个字节是交易的版本号，以小端存储
        version = Tx.little_endian_to_int(s.read(4))
        print(f"tx version is :{version}")
        return None
然后我们把交易数据转换为 io 数据流，传入到 parse 接口看看执行结果:

hex_transaction = ''
stream = BytesIO(bytes.fromhex(hex_transaction))

#测试读取版本号
Tx.parse(stream)
上面代码运行后所得结果如下：

tx version is :1
下面我们看输入部分。输入相当于别人对你的转账，输出相当于你从自己的账号中转钱给别人。因此你必须有钱进入账户，你才能有钱转出账户。一次转账可能有多笔，因此交易中的输入数据可能需要分成多部分进行解读。假设你卖了一本书，顾客支付给你 50 块，如果他一次性转账给你 50，那么输入就只有 1 笔，如果他分三次转账，第一次 30，接下来两次转 10 块，那么输入就有 3 笔，更极端的是，如果他一次给你转 1 毛，那么这次交易的输入就有 500 笔，因此我们在解读输入数据时需要先读取这次输入有多少笔数据。

我们看看上面二进制数据中与输入相关部分：

'01000000 {
[01]813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d10000000\
06b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02\
207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631\
e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278a
}

feffffff02a135ef0100000000\
1976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc\
762dd5423e332166702cb75f40df79fea1288ac19430600
上面数据中{}圈住的部分就是交易对应的输入部分，在[]圈住部分表示输入的数量，从上面数值 01 看，目前只有 1 笔输入。这里有个问题，如果输入的笔数超过了一个字节那如何表示呢，例如输入 50 块，但对方通过以每笔 1 毛的方式支付，那么就有 500 笔，这个数值如何表示呢。

这里就使用一种叫可变整形的编码方式。如果数值小于 253，那么我们使用一个字节就能表示。如果数值在 253 到 2^16 -1 之间，那么第一个字节设置为 0xfd(253)，然后接下来用两个字节来表示。如果数值在 2 ^ 16 到 2 ^ 32 -1 之间，那么第一个字节设置为 0xfe，然后接下来使用 4 个字节来表示，如果数值在 2 ^ 32 到 2 ^64 -1，那么第一个字节设置为 0xff, 然后接下来用 8 个字节来表示，我们看看具体实现：

@classmethod
    def read_varint(cls, s):
        """
        根据第一个字节读取数据
        如果第一字节小于 0xfd，那么直接读取其数值，
        如果取值 0xfd，则读取后面两字节
        如果取值 0xfe ，读取后面 4 字节
        如果取值 0xff,读取后面 8 字节
        """
        i = s.read(1)[0]
        if i == 0xfd:
            return Tx.little_endian_to_int(s.read(2))
        elif i == 0xfe:
            return Tx.little_endian_to_int(s.read(4))
        elif i == 0xff:
            return Tx.little_endian_to_int(s.read(8))
        else:
            return i

    @classmethod
    def parse(cls, s):
        #数据流的前 4 个字节是交易的版本号，以小端存储
        version = Tx.little_endian_to_int(s.read(4))
        print(f"tx version is :{version}")
        input_num = Tx.read_varint(s)
        print(f"num for inputs is :{input_num}")
        return None
上面代码运行后输出结果如下：

tx version is :1
num for inputs is :1
另外我们实现写入变量整形的操作，代码如下：

   @classmethod
    def int_to_little_endian(cls, n, length):
        #将给定整形数值以小端格式存储成字节数组
        return n.to_bytes(length, 'little')

    @classmethod
    def encode_varint(cls, i):
        if i < 0xfd:
            return bytes([i])
        if i < 0x10000:
            return b'\xfd' + Tx.int_to_little_endian(i, 2)
        elif i < 0x100000000:
            return b'\xfe' + Tx.int_to_little_endian(i, 4)
        elif i < 0x10000000000000000:
            return b'\xff' + Tx.int_to_little_endian(i, 8)
        else:
            raise ValueError(f'integer too larger: {i}')
知道有几条输入后，下面我们对输入的数据格式进行解析，它包含 4 个部分：
1，上一次交易 ID
2，上一次交易索引
3，交易对应执行脚本(scriptSig)
4，交易序列号

上一次交易 ID是上一次交易数据执行 hash256 运算后结果，它的长度为 32 字节。上一次交易索引是 4 字节。执行脚本是比特币对应的智能合约代码，它可以被执行，其内容我们后面再探讨。这部分是可变长，因此它需要一个变量整形来标记其长度。最后中本聪设计序列号的作用是实现高频交易，但这个设计存在严重漏洞，交易部分对应二进制数据如下，我用{}标记出来：

0100000001
{ 813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d10000000
06b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02
207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631
e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff }
02a135ef0100000000
1976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc
762dd5423e332166702cb75f40df79fea1288ac19430600
下面我们实现输入对象，首先我们给出它的基本框架：

class TxIn:
    def __init__(self, prev_tx, prev_index, script_sig=None, sequence=0xffffffff):
        self.prev_tx = prev_tx
        self.prev_index = prev_index
        if script_sig is None:
            self.script = Script()
        else:
            self.script_sig = script_sig

        self.sequence = sequence

    def __repr__(self):
        return f"{self.prev_tx.hex()}:{self.prev_index}"

    @classmethod
    def parse(cls, s):
        #因为它是大端存储，所以数据要倒转过来
        prev_tx = s.read(32)[::-1]
        print(f"prev tx hash: {prev_tx}")
        prev_index = Tx.little_endian_to_int(s.read(4))
        print(f"prev index for input: {prev_index}")

        # 解析 script 对象，和 sequence 后面再实现
        script_sig = None
        sequence = 0xffffffff

        return cls(prev_tx, prev_index, script_sig, sequence)
然后我们修改一下 Tx 对象中 parse 接口，增加解析输入对象的代码：

 @classmethod
    def parse(cls, s):
        #数据流的前 4 个字节是交易的版本号，以小端存储
        version = Tx.little_endian_to_int(s.read(4))
        print(f"tx version is :{version}")
        input_num = Tx.read_varint(s)
        print(f"num for inputs is :{input_num}")
        inputs = []
        # 解析输入数据
        for _ in range(input_num):
            inputs.append(TxIn.parse(s))
        return None
然后我们继续运行代码进行测试，运行后输出结果如下：

tx version is :1
num for inputs is :1
prev tx hash: b'\xd1\xc7\x89\xa9\xc6\x03\x83\xbfq_?j\xd9\xd1K\x91\xfeU\xf3\xde\xb3i\xfe]\x92\x80\xcb\x1a\x01y?\x81'
prev index for input: 0
下面我们看交易中的输出部分，所谓输出就是你花了多少钱，例如一笔交易中你花了 50 元，分别用 20 元卖了一个杯子，10 元买了牙刷，10 元买了手纸，那么这次交易就有三笔输出。输出部分的数据也是以一个变量整形开头，用来表明有多少笔输出。每个输出对象包含两部分内容，分别是花费的数值和脚本公钥(ScriptPubKey)。其中花费数值对应的单位是1/00,000,000 个比特币，这个字段占据 8 个字节。第二个字段脚本公钥用于获取执行支付脚本的权限，只有资产的所有人私钥能对应到这个公钥然后获得脚本的执行权限。

在上面给的数据例子中，我们将用{}把输出标注出来：

0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d10000000
06b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02
207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631
e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff0 
{
2a135ef0100000000
1976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac
}
99c39800000000001976a9141c4bc
762dd5423e332166702cb75f40df79fea1288ac19430600
我们看看 输出的基本框架:

class TxOut:
    def __init__(self, amount, script_pubkey):
        self.amount = amount
        self.script_pubkey = script_pubkey

    def __repr__(self):
        return f"{self.amount}:{self.script_pubkey}"

    @classmethod
    def parse(cls, s):
        amount = Tx.little_endian_to_int(s.read(8))
        print(f"amount for output is :{amount}")
        # 获取脚本公钥，后面才实现
        script_pubkey = 0 #Script.parse(s)
        return cls(amount, script_pubkey)
我们修改 Tx 中 parse 方法:

 @classmethod
    def parse(cls, s, testnet=False):
        #数据流的前 4 个字节是交易的版本号，以小端存储
        version = Tx.little_endian_to_int(s.read(4))
        print(f"tx version is :{version}")
        input_num = Tx.read_varint(s)
        print(f"num for inputs is :{input_num}")
        inputs = []
        # 解析输入数据
        for _ in range(input_num):
            inputs.append(TxIn.parse(s))

        output_nums = Tx.read_varint(s)
        outputs = []
        for _ in range(output_nums):
            outputs.append(TxOut.parse(s))
        return cls(version, inputs, outputs, None, testnet=testnet)
我们这次不能执行代码，因为我们在输入TxInput 中的解析还没有完全实现，后面我们完成执行脚本的解析后才好完成当前代码。下面我们看看最后一部分 LockTime，中本聪设置这个字段的目的在于实现高频交易，因为如果每次交易的数据要加入区块链速度就会非常慢，这个字段是为了加快速度但是却存在漏洞，它的大小为 4 字节，位于交易数据的末尾：

'0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac{19430600}
我们看看如何解析该字段：

@classmethod
    def parse(cls, s, testnet=False):
        #数据流的前 4 个字节是交易的版本号，以小端存储
        version = Tx.little_endian_to_int(s.read(4))
        print(f"tx version is :{version}")
        input_num = Tx.read_varint(s)
        print(f"num for inputs is :{input_num}")
        inputs = []
        # 解析输入数据
        for _ in range(input_num):
            inputs.append(TxIn.parse(s))

        output_nums = Tx.read_varint(s)
        outputs = []
        for _ in range(output_nums):
            outputs.append(TxOut.parse(s))


        #最后 4 字节对应 locktime
        locktime = Tx.little_endian_to_int(s.read(4))
        return cls(version, inputs, outputs, locktime, testnet=testnet)
由于上面代码中，区块链只能合约脚本的解析还没有实现，因此代码还不能顺利运行，下一节我们看看怎么处理。

