import captcha
import time


if __name__ == '__main__':
    while not captcha.captcha_false:
        captcha.serious_captcha(2)
        time.sleep(1)
# 验证码生成器，生成几条改数字
