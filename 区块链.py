import json
import random
import string
import hashlib
import time

from threading import Thread
from decimal import Decimal


# 区块类
class Block(object):
    # 一个区块有七个基本的属性, 分别是序号, id, 上一个区块id, 随机数, 难度系数, 时间戳, 还有一个区块体, 记录了交易信息
    def __init__(self):
        self.index = None
        # 区块的id
        self.hash = None
        self.previous_hash = None
        self.nonce = None
        self.difficulty = None
        self.timestamp = None
        self.transaction_data = None

    # 以字典的形式记录这个区块的信息, 并返回
    def get_block_info(self):
        block_info = {
            'Index': self.index,
            'Hash': self.hash,
            'Previous_hash': self.previous_hash,
            'Nonce': self.nonce,
            'Difficulty': self.difficulty,
            'Timestamp': self.timestamp,
            'Transaction_data': self.transaction_data,
        }
        return block_info


# 矿工类
class Pitman(object):
    # 定义矿工的挖矿方法, 需要的参数为该区块的序号, 之前的id, 交易信息
    def mine(self, index, previous_hash, transaction_data):
        # print('我要开始挖了')
        # 开始时间
        begin_time = time.time()

        block = Block()
        block.index = index
        block.previous_hash = previous_hash
        block.transaction_data = transaction_data
        block.timestamp = time.time()
        # 根据之前的id和交易信息生成这个区块的id和随机数, 还有困难系数
        block.difficulty, block.hash, block.nonce = self.gen_hash(previous_hash, transaction_data)

        # 结束时间
        end_time = time.time()
        # 花费的时间
        spend_time = end_time - begin_time
        # print('我挖完了')

        return block, spend_time

    @staticmethod
    def gen_hash(previous_hash, transaction_data):
        # 随机数, 从1到99999随机
        nonce = random.randrange(1, 99999)

        difficulty = 0
        guess = str(previous_hash) + str(nonce) + transaction_data
        res = hashlib.sha256(guess.encode()).hexdigest()
        # while (int(res[-1]) % 2) != 0:
        while res[-1] != '0':
            difficulty += 1
            nonce += difficulty
            guess = previous_hash + str(nonce) + transaction_data
            res = hashlib.sha256(guess.encode()).hexdigest()

        return difficulty, res, nonce


# 自定义线程类
class MyThread(Thread):
    def __init__(self, target, args=()):
        super(MyThread, self).__init__()
        self.func = target
        self.arg = args
        # self.result = None

    def run(self):
        self.result = self.func(*self.arg)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            print('自定义线程获取结果时发生了错误:', e)
            return None


# 首先, 创建一个区块链类
class BlockChain(object):
    def __init__(self, hash_num):
        # 存储区块链对象, 区块的容器
        self.chain_list = []

        # 矿工的容器
        self.pitman_list = []

        # 然后再容器中填入6个矿工
        for i in range(6):
            self.pitman_list.append(Pitman)

        # 存储每个阶段产生的区块
        self.result_list = []

        # 创建区块的方法,  如果当前生成的区块为第一个区块，则产生创世区块
        self.gen_block(hash_num)

    # 获取最后一个区块
    @property
    def get_last_block(self):
        if len(self.chain_list):
            return self.chain_list[-1]
        return None

    # 随机生成一份交易信息, 交易信息就是json字符串
    def get_trans(self):
        dict_data = {
            # random.sample可以从一个序列中随机获取指定数量的元素
            'sender': ''.join(random.sample(string.ascii_letters + string.digits, 8)),
            'recipient': ''.join(random.sample(string.ascii_letters + string.digits, 8)),
            # 相当于random.choice(range(1, 10000))
            'amount': random.randrange(1, 10000),
    }

        return json.dumps(dict_data)

    # 生成新区块的方法
    def gen_block(self, initial_hash=None):
        # 根据传参判断是否是创世区块

        # 如果是创世区块
        if initial_hash:
            # 先用区块类定义一个区块
            block = Block()
            # 然后对创建好的对象的实例属性进行设置
            block.index = 0
            block.nonce = random.randrange(0, 99999)
            block.previous_hash = '0'
            # 写到此, 我并不知道这个0是怎么来的, 以后是不是还要赋其他值?
            # 已经了解了, 0就是创世区块, 第一个, 所以是0

            block.difficulty = 0
            # 区块的交易信息
            block.transaction_data = self.get_trans()

            # 哈希值
            # guess = f'{block.previousHash}{block.nonce}{block.transactionData}'.encode()
            # 这个写法我没有看懂,
            # 看懂了, 是字符串格式化的另一种写法: f写法
            guess = str(block.index) + str(block.nonce) + block.previous_hash
            block.hash = hashlib.sha256(guess.encode()).hexdigest()

            block.timestamp = time.time()

            self.chain_list.append(block)

        # 如果不是创世区块
        else:
            # 先启动六个矿工开始挖矿
            for pitman in self.pitman_list:
            # for i in range(len(self.pitman_list)):
                # todo: 参数先不写, 以后在写
                t = MyThread(target=pitman.mine, args=(pitman,
                                                       len(self.chain_list),
                                                       # 获取当前这个区块链的最后一个区块的id
                                                       self.get_last_block.get_block_info()['Hash'],
                                                       # 获取交易信息
                                                       self.get_trans()))

                # t = MyThread(target=self.pitman_list[i].mine, )
                t.start()
                t.join()

                # 存储挖出来的区块
                self.result_list.append(t.get_result())

            print("All blocks generated by pitmen:")
            # 挖完了之后就该打印挖到的区块了
            # 上一个循环是同时启动六个矿工的线程开始运行, 等运行都完毕之后, 才开始继续主程序的运行, 是这样的吗?
            for result in self.result_list:
                print(result[0].get_block_info())

            # 获取新的区块
            # 先找到这个符合标准的区块

            # 先取出来第一个挖出来的区块
            first_block = self.result_list[0][0]
            # 再获取第一个区块计算耗费的时间, 转换成标准小数
            min_time = Decimal(self.result_list[0][1])

            # 去寻找那个用时最短的矿工挖出来的区块
            for i in range(1, len(self.result_list)):
                if Decimal(self.result_list[i][1]) < min_time:
                    first_block = self.result_list[i][0]

            # 找到以后存储
            self.chain_list.append(first_block)
            # 清空结果列表
            self.result_list = []

    def show_chain(self):
        for block in self.chain_list:
            print(block.get_block_info())


if __name__ == '__main__':
    chain = BlockChain(1)
    for i in range(20):
        chain.gen_block()
    chain.show_chain()
