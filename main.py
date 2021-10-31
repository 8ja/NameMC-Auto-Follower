from bs4 import BeautifulSoup
import json
import time
from colorama import Fore, Style
import undetected_chromedriver.v2 as uc
from discord_webhook import DiscordWebhook, DiscordEmbed

# Created by Jam#1090, sorry for dogshit code :)

def main():
    # Get Config Info
    with open('config.json') as f:
        data = json.load(f)
        discordWebhook = data['discord-webhook'] # Discord Webhook Input
        inputFile = data['input-file'] # File To Take Names To Follow
        namemcEmail, namemcPassword = data['namemc-email'], data['namemc-password'] # NameMC Login Information
        f.close()

    def success(text):
        print(f"{Style.RESET_ALL}[{Style.BRIGHT}{Fore.GREEN}+{Style.RESET_ALL}] {text}")
        webhook = DiscordWebhook(url=discordWebhook, rate_limit_retry=True, content=text)
        webhook.execute()

    def info(text):
        print(f"{Style.RESET_ALL}[{Style.BRIGHT}+{Style.RESET_ALL}] {text}")
        webhook = DiscordWebhook(url=discordWebhook, rate_limit_retry=True, content=text)
        webhook.execute()

    def error(text):
        print(f"{Style.RESET_ALL}[{Style.BRIGHT}{Fore.RED}+{Style.RESET_ALL}] {text}")
        webhook = DiscordWebhook(url=discordWebhook, rate_limit_retry=True, content=text)
        webhook.execute()


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
            selected_profile = soup.find('span', {'class': 'namemc-rank namemc-rank-10'}).getText()
            info(f"You have successfully logged in with the NameMC profile {selected_profile}.\nIf this is incorrect, change your selected profile on NameMC.com.")

            # Begin Following
            with open(inputFile) as f:
                names = f.read().splitlines()
                success(f"Loaded {len(names)} names from {inputFile}.")
                f.close()
            pos = 1
            for name in names:
                driver.get(f"https://namemc.com/{name}")
                try:
                    driver.find_element_by_css_selector('#followMenuButton').click()
                    driver.find_element_by_css_selector('#header > div.container.mt-3 > div > div.col > div > div > form > div > div > button:nth-child(1)').click()
                    success(f'Successfully followed {name} | {pos}/{len(names)}')
                except:
                    while True:
                        error(f"Failed to follow {name}. | {pos}/{len(names)}")
                        soup = BeautifulSoup(driver.page_source, features="lxml")
                        if soup.find('samp', {"class": "font-weight-bold"}):
                            ratelimitText = soup.find('samp', {"class": "font-weight-bold"}).getText()
                            num = ""
                            for char in ratelimitText:
                                if char.isdigit():
                                    num = num + char
                            error(f"Ratelimit Detected. Waiting {num} seconds.")
                            time.sleep(int(num))
                        else:
                            break
                        driver.get(f"https://namemc.com/{name}")
                        try:
                            driver.find_element_by_css_selector('#followMenuButton').click()
                            driver.find_element_by_css_selector('#header > div.container.mt-3 > div > div.col > div > div > form > div > div > button:nth-child(1)').click()
                            success(f'Successfully followed {name} | {pos}/{len(names)}')
                            break
                        except:
                            pass
                pos += 1
                

if __name__ == "__main__":
    main()