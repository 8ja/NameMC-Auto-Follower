from bs4 import BeautifulSoup
import json
import time
import requests
from colorama import Fore, Style
import undetected_chromedriver.v2 as uc
from discord_webhook import DiscordWebhook, DiscordEmbed

# Created by Jam#1090, sorry for dogshit code :)


def main():
    # Get Config Info
    with open('config.json') as f:
        data = json.load(f)
        discordWebhookToggle = data['enable-webhooks'] # Discord Webhook Toggle
        discordWebhook = data['discord-webhook'] # Discord Webhook Input
        inputFile = data['input-file'] # File To Take Names To Follow
        namemcEmail, namemcPassword = data['namemc-email'], data['namemc-password'] # NameMC Login Information
        f.close()

    def valid(name):
        r = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{name}")
        if r.status_code == 200:
            return True
        else:
            return False

    def success(text):
        print(f"{Style.RESET_ALL}[{Style.BRIGHT}{Fore.GREEN}+{Style.RESET_ALL}] {text}")
        if discordWebhookToggle:
            webhook = DiscordWebhook(url=discordWebhook, rate_limit_retry=True, content=text)
            webhook.execute()

    def info(text):
        print(f"{Style.RESET_ALL}[{Style.BRIGHT}+{Style.RESET_ALL}] {text}")
        if discordWebhookToggle:
            webhook = DiscordWebhook(url=discordWebhook, rate_limit_retry=True, content=text)
            webhook.execute()

    def error(text):
        print(f"{Style.RESET_ALL}[{Style.BRIGHT}{Fore.RED}+{Style.RESET_ALL}] {text}")
        if discordWebhookToggle:
            webhook = DiscordWebhook(url=discordWebhook, rate_limit_retry=True, content=text)
            webhook.execute()

    def ratelimited(t):
        t = int(t)
        error(f"Ratelimited for {str(t)} seconds.")
        while t:
            print(f"{Style.RESET_ALL}[{Style.BRIGHT}{Fore.RED}+{Style.RESET_ALL}] Ratelimited. Please wait {str(t)} more seconds.", end="\r")
            time.sleep(1)
            t -= 1


    # Init undetected_chromedriver & login to NameMC.
    driver = uc.Chrome()
    with driver:
        driver.get('https://namemc.com/login')
        emailInput = driver.find_element_by_xpath('//*[@id="email"]')
        emailInput.send_keys(namemcEmail)
        passwordInput = driver.find_element_by_xpath('//*[@id="password"]')
        passwordInput.send_keys(namemcPassword)
        loginButton = driver.find_element_by_xpath('/html/body/main/div/div/div/div/div[2]/form/div/button')
        loginButton.click()
        try:
            driver.find_element_by_css_selector('body > main > div > div > div > div > div.mb-1 > form > div > button')
            error("The email address or password is incorrect.")
            exit()
        except:
            soup = BeautifulSoup(driver.page_source, features="lxml")


            # Begin Following
            with open(inputFile) as f:
                names = f.read().splitlines()
                success(f"Loaded {len(names)} names from {inputFile}.")
                f.close()
            pos = 1
            for name in names:
                if valid(name):
                    driver.get(f"https://namemc.com/{name}")
                    try:
                        driver.find_element_by_css_selector('#followMenuButton').click()
                        driver.find_element_by_css_selector('#header > div.container.mt-3 > div > div.col > div > div > form > div > div > button:nth-child(1)').click()
                        soup = BeautifulSoup(driver.page_source, features="lxml")
                        if soup.find("samp", {"class": "font-weight-bold"}):
                            raise Exception("Ratelimited")
                        else:
                            success(f'{pos}/{len(names)} | Successfully followed {name}')
                    except:
                        while True:
                            soup = BeautifulSoup(driver.page_source, features="lxml")
                            if soup.find('samp', {"class": "font-weight-bold"}): #ratelimit check
                                error(f"Failed to follow {name}. | {pos}/{len(names)}")
                                ratelimitText = soup.find('samp', {"class": "font-weight-bold"}).getText()
                                num = ""
                                for char in ratelimitText:
                                    if char.isdigit():
                                        num = num + char
                                ratelimited(num)
                            else:
                                error(f"{pos}/{len(names)} | {name} already followed.")
                                break
                            driver.get(f"https://namemc.com/{name}")
                            try:
                                driver.find_element_by_css_selector('#followMenuButton').click()
                                driver.find_element_by_css_selector('#header > div.container.mt-3 > div > div.col > div > div > form > div > div > button:nth-child(1)').click()
                                success(f'{pos}/{len(names)} | Successfully followed {name}')
                                break
                            except:
                                pass
                else:
                    error(f"{pos}/{len(names)} | Skipped {name} as it's invalid.")
                pos += 1
                

if __name__ == "__main__":
    main()
