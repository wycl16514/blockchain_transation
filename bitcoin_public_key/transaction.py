import hashlib
from io import BytesIO
def hash256(s):
    # 连续进行两次sha256运算
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

class TxFetcher:
    cache = {}
    @classmethod
    def get_url(cls, testnet=False):
        return 'http://testnet.pro'


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
    def little_endian_to_int(cls, b):
        # 读入数据流读入 4 字节，将其以小端方式存储，然后解读成一个整形 int 数值
        return int.from_bytes(b, 'little')

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

class Script:
    # 后面实现
    def __init__(self):
        pass

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



hex_transaction = '0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf8303c6a989c7d10000000\
06b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccfcf21320b0277457c98f02\
207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8e10615bed01210349fc4e631\
e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278afeffffff02a135ef0100000000\
1976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88ac99c39800000000001976a9141c4bc\
762dd5423e332166702cb75f40df79fea1288ac19430600'


#print(hex_transaction[82])
stream = BytesIO(bytes.fromhex(hex_transaction))
#
# #测试读取版本号
Tx.parse(stream)