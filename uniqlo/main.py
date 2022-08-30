import set_time
import monitor
import warnings

warnings.filterwarnings("ignore")

if __name__ == '__main__':
    mode = int(input('1.定点抢购模式 2.补货模式====>'))
    if mode == 1:
        set_time.main()
    elif mode == 2:
        monitor.main()
