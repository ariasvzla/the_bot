import undetected_chromedriver as uc
import time


driver = uc.Chrome()
options = uc.ChromeOptions()
options.add_argument("--auto-open-devtools-for-tabs")
driver.get("https://bot.solesbot.ai")
time.sleep(90)
