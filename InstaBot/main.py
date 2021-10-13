#pylint: disable=broad-except,global-statement,unnecessary-lambda
import requests
from sys import stdout
from time import sleep
from getpass import getpass
from random import choice, shuffle
from selenium import webdriver, common
from webdriver_manager.utils import ChromeType
from selenium.webdriver.common.keys import Keys
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

TOTAL = 0

class InstaBot(object):
    self_following = []
    self_username = None
    all_users_tagged_once = False

    def __init__(self, browser_t: int, browser, must_stop_after_first_cycle=False):
        driver_gen_funcs = [
            lambda ce: webdriver.Chrome(ce),
            lambda ci: webdriver.Chrome(ci),
            lambda f:  webdriver.Firefox(executable_path=f),
            lambda ie: webdriver.Ie(ie),
            lambda e:  webdriver.Edge(e)
        ]
        self.driver = driver_gen_funcs[browser_t-1](browser) #webdriver.Firefox()
        self.driver.implicitly_wait(3)

        self.instagram_base_url = 'https://www.instagram.com/'

        self.must_stop_after_first_cycle = must_stop_after_first_cycle

    def log_in(self, username_elem, password_elem, username, password):
        username_elem.send_keys(username)
        password_elem.send_keys(password)

        username_elem.submit()
        self.driver.implicitly_wait(7)

    def log_in_native(self, username, password):
        login_url = self.instagram_base_url+'accounts/login/'
        self.driver.get(login_url)

        username_elt = self.driver.find_element_by_name("username")
        password_elt = self.driver.find_element_by_name("password")

        self.log_in(username_elt, password_elt, username, password)
        print("usuario: ", "O nome de usuário inserido não pertence a uma conta" in self.driver.page_source)
        print("senha: ", "Sua senha está incorreta" in self.driver.page_source)

        self.set_username()

    def log_in_via_facebook(self, username, password):
        login_url = self.instagram_base_url+'accounts/login/'
        self.driver.get(login_url)

        facebook_login_btn = self.driver.find_element_by_css_selector('.sqdOP.yWX7d.y3zKF')
        facebook_login_btn.click()

        facebook_username_elem = self.driver.find_element_by_name("email")
        facebook_password_elem = self.driver.find_element_by_name("pass")

        self.log_in(facebook_username_elem, facebook_password_elem, username, password)

        self.set_username()

    def set_username(self):
        try:
            profile_btn = self.driver.find_element_by_css_selector('a.gmFkV')
        except common.exceptions.NoSuchElementException as e:
            self.set_username()
            return
        
        self.self_username = profile_btn.get_attribute('href').split("/")[-2]

    def follow_user(self, user):
        self.driver.get(self.instagram_base_url+user)

        try:
            follow_btn = self.driver.find_element_by_css_selector("._5f5mN.jIbKX._6VtSN.yZn4P")
            follow_btn.click()

            return True
        except Exception:
            return False

    def scroll_down(self):
        script = ("var elem = document.getElementsByClassName('isgrP');elem[0].scrollBy(0,10000);")
        self.driver.execute_script(script)

    def set_self_following(self):
        self.driver.get(self.instagram_base_url+self.self_username)

        #self.driver.find_element_by_css_selector('a[href="/%s/following/"]'%self.self_username).click()
        self.driver.find_element_by_css_selector('a[href="/%s/followers/"]'%self.self_username).click()

        for _ in range(15):
            sleep(3)
            self.scroll_down()

        self.self_following = list(map(lambda x: x.get_attribute('title'), self.driver.find_elements_by_css_selector('a.FPmhX')))

    def get_followers_count(self, user):
        self.driver.get(self.instagram_base_url+user)

        try:
            number_of_followers = self.driver.find_element_by_css_selector('a[href="/%s/followers/"] .g47SY' % user)
        except Exception as e:
            number_of_followers = self.driver.find_element_by_css_selector('ul.k9GMp li.Y8-fY:nth-child(2) .g47SY')
        number_of_followers = number_of_followers.get_attribute("title").replace('.', '')
        return int(number_of_followers)

    def get_following_count(self, user):
        self.driver.get(self.instagram_base_url+user)
        try:
            number_of_following = self.driver.find_element_by_css_selector('a[href="/%s/following/"] .g47SY' % user).text
        except Exception:
            number_of_following = self.driver.find_element_by_css_selector('ul.k9GMp li.Y8-fY:nth-child(3) .g47SY').text
        return int(number_of_following.replace('.', '')) if 'mil' not in number_of_following else int(number_of_following.replace('.', ''))*1000

    def get_follow_ratio(self, user: str) -> bool:
        return self.get_followers_count(user) / self.get_following_count(user)
    
    def is_user_valid(self, user: str) -> bool:
        headers = {
            'Host': 'www.instagram.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers'
        }
        
        status_code = requests.get(f"https://www.instagram.com/{user[1]}/", headers=headers).status_code
        return status_code != 404

    def build_message(self, text_to_send, number_of_people, preselected_users):
        message = [text_to_send]
        while number_of_people > 0:
            if preselected_users:
                shuffle(preselected_users)
                preselected_users.sort(key=lambda x: x[0])
                random_user = preselected_users[0]
                
                if random_user[0] == 1 and self.must_stop_after_first_cycle:
                    self.all_users_tagged_once = True
                    break
                
                if random_user[1] in message:
                    continue
                else:
                    if not self.is_user_valid(random_user) or random_user[1] == "":
                        continue

                    random_user[0] += 1
                    random_user = random_user[1]
            else:
                random_user = choice(self.self_following)

                if random_user in message or self.get_follow_ratio(random_user) > 3:
                    continue
        
            message.append(random_user)#message.append(random_user) CHANGED
            number_of_people -= 1
        return ' '.join(message)

    def send_message(self, promo_url, message):
        if not (self.driver.current_url == promo_url):
            print(promo_url)
            self.driver.get(promo_url)
        sleep(3)

        try:
            message_input = self.driver.find_element_by_css_selector('.Ypffh')
            message_input.send_keys(message)
        except Exception:
            message_input = self.driver.find_element_by_css_selector('.Ypffh')
            message_input.send_keys(message)
        
        try:
            send_btn = self.driver.find_element_by_css_selector('form.X7cDz button.sqdOP')
            send_btn.click()
        except Exception:
            send_btn = self.driver.find_element_by_css_selector('form.X7cDz button.sqdOP')
            send_btn.click()


    def send_messages(self, promo_url, text_to_send, preselected_users, number_of_people, interval):
        global TOTAL
        print("OXE, CHEGOU AQUI?", self.all_users_tagged_once, self.must_stop_after_first_cycle)
        if not (self.self_following or preselected_users):
            self.set_self_following()			

        while True:
            if self.all_users_tagged_once and self.must_stop_after_first_cycle:
                break
            message = self.build_message(text_to_send, number_of_people, preselected_users)
            try:
                self.send_message(promo_url, message)
                TOTAL += 1
            #pylint: disable=broad-except
            except Exception:
                self.driver.execute_script("location.reload(true);")
                sleep(3)
            
            sleep(interval)
        
    def close_browser(self):
        self.driver.close()

def process_preselected_users(list_of_users: list):
    return [[0, c.strip()] for c in list_of_users]

browser_gen_funcs = [  
    lambda: ChromeDriverManager().install(),
    lambda: ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),
    lambda: GeckoDriverManager().install(),
    lambda: IEDriverManager().install(),
    lambda: EdgeChromiumDriverManager().install()
]
