from bootbox_bot import BootboxBot

bot = BootboxBot()

try:
    bot.open()
    bot.login()
    bot.run_flow()
finally:
    bot.close()