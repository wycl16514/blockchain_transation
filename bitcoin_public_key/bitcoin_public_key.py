import hashlib

class LimitFieldElement:  # 实现有限域的元素
    def __init__(self, num, order):
        """
        order 表示集合元素的个数，它必须是一个素数，不然有限域的性质不能满足
        num 对应元素的数值
        """

        if order <= num < 0:
            err = f"元素 {num} 数值必须在0到 {order - 1} 之间"
            raise ValueError(err)
        self.order = order
        self.num = num

    def __repr__(self):
        return f"LimitFieldElement_{hex(self.order).zfill(32)}_({hex(self.num).zfill(32)})"

    def __eq__(self, other):
        if other is None:
            return False
        return self.num == other.num and self.order == other.order

    def __ne__(self, other):
        if other is None:
            return True

        return self.num != other.num or self.order != other.order

    def __add__(self, other):
        """
        有限域元素的"+"操作，它是在普通加法操作的基础上，将结果对集合中元素个数求余
        """
        if self.order != other.order:
            raise TypeError("不能对两个不同有限域集合的元素执行+操作")
        # 先做普通加法，然后在结果基础上相对于集合元素的个数做求余运算
        num = (self.num + other.num) % self.order
        """
        这里使用__class__而不是LimitFieldElemet是为了后面实现类的继承考虑，
        后面我们实现的对象需要继承与这个类
        """
        return self.__class__(num, self.order)

    def __sub__(self, other):
        if self.order != other.order:
            raise TypeError("不能对两个不同有限域的元素执行减法操作")
        num = (self.num - other.num) % self.order
        return __class__(num, self.order)

    def __mul__(self, other):
        """
        有限域元素进行"*"操作时，先执行普通的乘法操作，然后将结果针对集合元素的个数进行求余
        """
        if self.order != other.order:
            raise TypeError("不能对两个不同有限域集合的元素执行*操作")

        num = (self.num * other.num) % self.order
        return self.__class__(num, self.order)

    def __pow__(self, power, modulo=None):
        """
        指数操作是先执行普通四则运算下的指数操作，再将所得结果针对集合元素个数求余
        """
        while power < 0:
            power += self.order
        num = pow(self.num, power, self.order)
        return self.__class__(num, self.order)

    def __truediv__(self, other):
        if self.order != other.order:
            raise TypeError("不能对两个不同有限域集合的元素执行*操作")
        # 通过费马小定理找到除数的对应元素
        #negative = (other.num ** (self.order - 2)) % self.order
        #这里必须使用系统提供的pow函数，因为它经过了算法优化，我们上面直接算，当数值很大时效率很低，代码会卡住
        negative = pow(other.num, self.order - 2, self.order)
        num = (self.num * negative) % self.order
        return self.__class__(num, self.order)

    def __rmul__(self, scalar):
        #实现与常量相乘
        num = (self.num * scalar) % self.order
        return __class__(num, self.order)


class EllipticPoint:
    def __init__(self, x, y, a, b):
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        """
        x == None, y == None对应点"0"
        """
        if x is None or y is None:
            return

        """
        a, b为椭圆曲线方程 y^2 = x ^ 3 + ax + b
        对于区块链的椭圆曲线a取值为0，b取值为7,其专有名称为secp256k1
        由此在初始化椭圆曲线点时，必须确保(x,y)位于给定曲线上
        """
        t = y ** 2
        t = x ** 3
        t = a * x
        if y ** 2 != x ** 3 + a * x + b:
            raise ValueError(f'({x}, {y}) is not on the curve')

    def __eq__(self, other):
        """
        两个点要相等，我们不能只判断x,y是否一样，必须判断他们是否位于同一条椭圆曲线
        """
        return self.x == other.x and self.y == other.y and self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y or self.a != other.a or self.b != other.b

    def __add__(self, other):
        if self == other and self.y == 0 * self.x:
            #对应椭圆曲线顶部点的切线
            return self.__class__(None, None, self.a, self.b)

        """
        实现"+"操作，首先确保两个点位于同一条曲线，也就是他们对应的a,b要相同
        """
        if self.a != other.a or self.b != other.b:
            raise TypeError(f"points {self}, {other} not on the same curve")

        # 如果其中有一个是"0"那么"+"的结果就等于另一个点
        if self.x is None:
            return other
        if other.x is None:
            return self

        """
        两点在同一直线上，也就是x相同，y不同
        """
        if self.x == other.x and self.y != other.y:
            return __class__(None, None, self.a, self.b)

        """
        计算两点连线后跟曲线相交的第3点，使用韦达定理
        """
        x1 = self.x
        y1 = self.y
        x2 = other.x
        y2 = other.y
        if self == other:
            # 如果两点相同，根据微分来获得切线的斜率
            t1 = 3 * self.x ** 2 + self.a
            t2 = 2 * self.y
            t3 = t1 / t2
            k = (3 * self.x ** 2 + self.a) / (2 * self.y)
        else:
            k = (y2 - y1) / (x2 - x1)

        x3 = k ** 2 - x1 - x2
        y3 = k * (x1 - x3) - y1

        return __class__(x3, y3, self.a, self.b)

    def __repr__(self):
        return f"EllipticPoint(x:{self.x},y:{self.y},a:{self.a}, b:{self.b})"

    # def __rmul__(self, scalar):
    #     #如果常量是0，那么就返回椭圆曲线"0"点
    #     result = self.__class__(None, None, self.a, self.b)
    #     #自加给定次数
    #     for _ in range(scalar):
    #         result += self
    #
    #     return result

    def __rmul__(self, scalar):
        #二进制扩展
        coef = scalar
        current = self
        result = self.__class__(None, None, self.a, self.b)
        while coef:
            if coef & 1: #如果当前比特位是1，那么执行加法
                result += current
            current += current  #如果上次比特位的位置在k，那么下次比特位的位置变成k+1，2^(k+1)*G 等价于2^k*G + 2^k * G
            coef >>= 1

        return result


P = 2**256 - 2**32 - 977


class S256Field(LimitFieldElement):
    def __init__(self, num, order=None):
        # 参数写死即可
        super().__init__(num, P)

    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)

    def sqrt(self):
        return self ** ((P+1) // 4)


N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141


def hash160(s):
    #先进行sha256哈希，然后再进行ripemd160哈希
    return hashlib.new("ripemd160", hashlib.sha256(s).digest()).digest()


#用于base58编码的字符集，这里去掉了数字 1 和大写字母I,数字 0 和大写字母O
BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def encode_base58(s):
    count = 0
    for c in s: # 统计输入的二进制数据在开头有多少个 0
        if c == 0:
            count += 1
        else:
            break

    num = int.from_bytes(s, 'big')
    prefix = '1' * count #将开头的数字 0 用字符'1'替换
    result = ''
    while num > 0:
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result

    return prefix + result


def hash256(s):
    # 连续进行两次sha256运算
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()


def encode_base58_checksum(b):
    return encode_base58(b + hash256(b)[:4])


class S256Point(EllipticPoint):
    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(0), S256Field(7)
        if type(x) == int:
            super().__init__(S256Field(x), S256Field(y), a, b)
        else:
            # 如果x,y 是None，那么直接初始化椭圆曲线的0点
            super().__init__(x, y, a, b)

    def __repr__(self):
        if self.x is None:
            return 'S256Point(infinity)'

        return f'S256Point({self.x}, {self.y})'

    def __rmul__(self, k):
        k = k % N
        return super().__rmul__(k)

    def sec(self, compressed=True):
        """
        将32字节的x,y转换成大端形式数组，然后两个数组合成一个，最后在合成的数组前头插入一个字节0x04
        """
        if compressed:
            if self.y.num % 2 == 0:
                return b'\x02' + self.x.num.to_bytes(32, 'big')
            else:
                return b'\x03' + self.num.to_bytes(32, 'big')
        return b'\x04' + self.x.num.to_bytes(32, 'big') + self.y.num.to_bytes(32, 'big')

    @classmethod
    def parse(clsse, sec_array):
        """
        如果是非压缩模式，那么直接得出公钥的x,y
        """
        if sec_array[0] == 4:
            x = int.from_bytes(sec_array[1:33], 'big')
            y = int.from_bytes(sec_array[33:65], 'big')
            return S256Point(x=x, y=y)

        # 首字节如果是2那么y的值是偶数，要不然就是奇数
        is_even = (sec_array[0] == 2)
        # 先获得x部分的值
        x = S256Field(int.from_bytes(sec_array[1:], 'big'))
        #计算 y ^ 2的值，也就是 x ^ 3 + 7
        y2 = x ** 3 + S256Field(7)
        # 计算开方，也就是计算 y2 ^ ((P+1)/4)
        y = y2.sqrt()
        if y.num % 2 == 0:
            even_y = y
            odd_y = S256Field(P - even_y.num)
        else:
            even_y = S256Field(P - y.num)
            odd_y = y

        if is_even:
            return S256Point(x, even_y)
        else:
            return S256Point(x, odd_y)

    def hash160(self, compressed=True):
        return hash160(self.sec(compressed))

    def address(self, compressed=True, testnet=False):
        h160 = self.hash160(compressed)
        if testnet:
            prefix = b'\x6f'
        else:
            prefix = b'\x00'

        return encode_base58_checksum(prefix + h160)





# s_bin = '7c076ff316692a3d7eb3c3bb0f8b1488cf72e1afcd929e29307032997a838a3d'
# s_bin_base58 = encode_base58(bytes.fromhex(s_bin))
# print(f"base58 encode: {s_bin_base58}")


G = S256Point(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798,
              0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)


#print(N * G)

privKey = 0x038109007313a5807b2eccc082c8c3fbb988a973cacf1a7df9ce725c31b14776
pubKey = privKey * G

# point = S256Point(pubKey.x.num, pubKey.y.num)
# print(f"public key: {point}")
# compress_pub_key = point.sec()
# print(", ".join(hex(b) for b in compress_pub_key))
#
# recover_pub_key = S256Point.parse(compress_pub_key)
# print(f"recover pub key: {recover_pub_key}")
#
# print(f"mainnet address is :{point.address(compressed=True,testnet=False)}")

class PrivateKey:
    def __init__(self, secret):
        self.secret = secret

    def wif(self, compressed=True, testnet=False):
        #先将私钥进行大端转换
        secret_bytes = self.secret.to_bytes(32, 'big')
        if testnet:
            #如果是测试网络的私钥则在开头增加字节0xef
            prefix = b'\xef'
        else:
            #如果是主网络则在开头增加字节0x80
            prefix = b'\0x80'
        if compressed:
            #如果要创建压缩格式的公钥，在末尾增加自己0x1
            suffix = b'\0x01'
        else:
            suffix = ''

        return encode_base58_checksum(prefix + secret_bytes + suffix)


private_key = PrivateKey(privKey)
wif_private_key = private_key.wif()
print(f"the wif for give private key is: {wif_private_key}")







