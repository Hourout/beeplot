import tensorflow as tf
import matplotlib.pyplot as plt
from collections import defaultdict
from IPython.display import clear_output
from tensorflow.keras.callbacks import Callback

def draw(metrics, logs, epoch, columns, iter_num, wait_num, figsize, cell_size, valid_fmt):
    if epoch%wait_num==0:
        clear_output(wait=True)
        plt.figure(figsize=figsize)
        for metric_id, metric in enumerate(metrics):
            plt.subplot((len(metrics)+1)//columns+1, columns, metric_id+1)
            if iter_num is not None:
                plt.xlim(1, iter_num)
            plt.plot(range(1, len(logs[metric])+1), logs[metric], label="train")
            if valid_fmt.format(metric) in logs:
                plt.plot(range(1, len(logs[metric])+1), logs[valid_fmt.format(metric)], label=valid_fmt.split('_')[0])
            plt.title(metric)
            plt.xlabel('batch')
            plt.legend(loc='center right')
        plt.tight_layout()
        plt.show()

class PlotMetricsOnBatch(tf.keras.callbacks.Callback):
    def __init__(self, metrics_name, columns=2, iter_num=None, mode=1, wait_num=1, figsize=None, cell_size=(6, 4),
                 valid_fmt="val_{}", eval_batch_num=None):
        tf.logging.set_verbosity(tf.logging.ERROR)
        self.metrics_name = metrics_name
        self.columns = columns
        self.iter_num = iter_num
        self.wait_num = wait_num
        self.figsize = figsize
        self.cell_size = cell_size
        self.valid_fmt = valid_fmt
        self.batch_logs = defaultdict(list)
        self.batch_num = 0
        self.eval_batch_num = eval_batch_num

    def on_batch_end(self, batch, logs=None):
        if self.mode==1:
            self.batch_num += 1
            for i in ['batch', 'size']:
                logs.pop(i)
            if self.validation_data is not None:
                if self.eval_batch_num is not None:
                    if self.batch_num%self.eval_batch_num==0:
                        loss_list = self.model.test_on_batch(self.validation_data[0],
                                                             [self.validation_data[i] for i in range(1, int(len(self.validation_data)/2))])
                        new_val_name = [self.valid_fmt.split('_')[0]+'_'+i for i in self.metrics_name]
                        for loss_value, new_name in zip(loss_list, new_val_name):
                            logs[new_name] = loss_value
            for old_name, new_name in zip(self.model.metrics_names, self.metrics_name):
                logs[new_name] = logs.pop(old_name)
#             print(self.batch_num, logs)
            

            self.metrics = list(filter(lambda x: x not in ['batch', 'size'], logs))
#             if self.figsize is None:
#                 self.figsize = (self.columns*self.cell_size[0], ((len(self.metrics)+1)//self.columns+1)*self.cell_size[1])
#             for metric in self.metrics:
#                 self.batch_logs[metric] += [logs[metric]]
#             draw(metrics=self.metrics, logs=self.batch_logs, epoch=self.batch_num, columns=self.columns,
#                  iter_num=self.iter_num, mode=self.mode, wait_num=self.wait_num, xlabel=self.xlabel,
#                  figsize=self.figsize, cell_size=self.cell_size, valid_fmt=self.valid_fmt)

    def on_train_end(self, logs=None):
        draw(metrics=self.metrics, logs=self.epoch_logs, epoch=self.wait_num, columns=self.columns,
             iter_num=self.iter_num, wait_num=self.wait_num,
             figsize=self.figsize, cell_size=self.cell_size, valid_fmt=self.valid_fmt)