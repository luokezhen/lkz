import tensorflow as tf


def line():
    # 准备数据
    x = tf.random_normal(shape=[100, 1], mean=0.5, stddev=0.25)

    y = tf.matmul(x, [[5.0]]) + 6.0

    # 建立模型
    w = tf.Variable([[1.0]])
    b = tf.Variable(1.0)
    y_pre = tf.matmul(x, w) + b

    # 计算损失
    # loss = tf.reduce_mean(tf.square(y_pre - y))
    loss = tf.reduce_mean(abs(y_pre - y))

    # 优化损失， 梯度下降
    lr = 0.1
    t = tf.train.GradientDescentOptimizer(learning_rate=lr).minimize(loss=loss)

    # 收集变量
    tf.summary.scalar(name='b', tensor=b)
    tf.summary.histogram(name='w', values=w)

    # 合并变量
    merge = tf.summary.merge_all()

    init_op = tf.global_variables_initializer()

    path = './tmp/summary/'

    with tf.Session() as sess:
        sess.run(init_op)

        # 建立事件文件
        f = tf.summary.FileWriter(logdir=path, graph=sess.graph)

        for i in range(500):
            sess.run(t)
            print(i, w.eval(), b.eval())
            summary = sess.run(merge)
            f.add_summary(summary=summary, global_step=i)


if __name__ == '__main__':
    line()





















