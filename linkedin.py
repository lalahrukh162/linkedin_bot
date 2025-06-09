import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
import time, random, csv, os, json, zipfile, shutil, streamlit as st
from config import PROXY_LIST, BATCH_SIZE, HEADLESS

JOB_TITLE = "Software Engineer"
LOCATION = "Pakistan"

class LinkedInBot:
    COOKIES_FOLDER = "cookies"

    def __init__(self, email, password, proxy=None):
        self.email = email
        self.password = password
        self.proxy = proxy or random.choice(PROXY_LIST)
        self.driver = None
        self.ext_dir = f"proxy_ext_{self.email.replace('@','_')}"
        self.ext_zip = f"proxy_auth_plugin_{self.email.replace('@','_')}.zip"
        os.makedirs(self.COOKIES_FOLDER, exist_ok=True)

    def get_cookies_path(self):
        return os.path.join(self.COOKIES_FOLDER, f"{self.email.replace('@', '_')}_cookies.json")

    def _create_proxy_extension(self, host, port, user, pwd):
        manifest = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": ["proxy","tabs","unlimitedStorage","storage","<all_urls>","webRequest","webRequestBlocking"],
            "background": {"scripts": ["background.js"]},
            "minimum_chrome_version": "22.0.0"
        }
        background_js = f"""
                    var config = {{mode: "fixed_servers",rules: {{singleProxy:{{scheme: "http",host: "{host}",port: parseInt({port})}},bypassList:["localhost"]}}}};
                    chrome.proxy.settings.set({{value:config,scope:"regular"}},()=>{{}});
                    function callbackFn(details) {{return {{authCredentials:{{username:"{user}",password:"{pwd}"}}}};}}
                    chrome.webRequest.onAuthRequired.addListener(callbackFn,{{urls:["<all_urls>"]}},['blocking']);
                    """
        shutil.rmtree(self.ext_dir, ignore_errors=True)
        os.makedirs(self.ext_dir, exist_ok=True)
        with open(os.path.join(self.ext_dir, 'manifest.json'), 'w') as f: json.dump(manifest, f)
        with open(os.path.join(self.ext_dir, 'background.js'), 'w') as f: f.write(background_js)
        with zipfile.ZipFile(self.ext_zip, 'w') as zp:
            zp.write(os.path.join(self.ext_dir, 'manifest.json'), 'manifest.json')
            zp.write(os.path.join(self.ext_dir, 'background.js'), 'background.js')
        return self.ext_zip

    def _cleanup_proxy_files(self):
        for path in (self.ext_dir, self.ext_zip):
            try:
                if os.path.isdir(path): shutil.rmtree(path)
                elif os.path.exists(path): os.remove(path)
            except: pass

    def setup_driver(self):
        opts = uc.ChromeOptions()
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-popup-blocking")
        opts.add_argument("--disable-notifications")
        if HEADLESS: opts.add_argument("--headless=new")

        if '@' in self.proxy:
            try:
                auth, server = self.proxy.split('@',1)
                u, p = auth.split(':',1)
                h, port = server.split(':',1)
                ext = self._create_proxy_extension(h, port, u, p)
                opts.add_extension(ext)
            except:
                opts.add_argument(f"--proxy-server={self.proxy}")
        else:
            opts.add_argument(f"--proxy-server={self.proxy}")

        self.driver = uc.Chrome(options=opts, use_subprocess=True)

    def human_type(self, el, text):
        for c in text:
            el.send_keys(c); time.sleep(random.uniform(0.05,0.3))

    def random_scroll(self):
        self.driver.execute_script(f"window.scrollBy(0,{random.randint(200,800)});")
        time.sleep(random.uniform(0.5,2.0))

    def random_delay(self, a=1.0, b=3.0):
        time.sleep(random.uniform(a,b))

    def login(self):
        self.driver.get("https://www.linkedin.com/login")
        self.random_delay(2,4)
        cookie_file = self.get_cookies_path()
        if os.path.exists(cookie_file):
            try:
                self.load_cookies(cookie_file)
                self.driver.get("https://www.linkedin.com/feed")
                WebDriverWait(self.driver,10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.scaffold-finite-scroll'))
                )
                return True
            except:
                pass
        return self.perform_login()

    def perform_login(self):
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.ID,'username')))
        user_f = self.driver.find_element(By.ID,'username'); self.human_type(user_f,self.email)
        self.random_delay(0.5,1.5)
        pwd_f = self.driver.find_element(By.ID,'password'); self.human_type(pwd_f,self.password)
        self.random_delay(0.5,1.0)
        self.driver.find_element(By.XPATH,"//button[@type='submit']").click()
        self.random_delay(3,5)
        try:
            WebDriverWait(self.driver,10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,'div.scaffold-finite-scroll'))
            )
            self.save_cookies()
            return True
        except:
            return False

    def save_cookies(self):
        cookies = self.driver.get_cookies()
        with open(self.get_cookies_path(),'w') as f:
            json.dump(cookies, f)

    def load_cookies(self, path):
        with open(path, "r") as f:
            cookies = json.load(f)
        
        self.driver.get("https://www.linkedin.com")
        self.random_delay(1, 2)  
        
        self.driver.delete_all_cookies()
        for cookie in cookies:
            if 'sameSite' in cookie and cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                cookie['sameSite'] = 'Lax'
            try:
                self.driver.add_cookie(cookie)
            except: pass
        self.random_delay(1, 2)

    def search_for_jobs(self):
        self.driver.get("https://www.linkedin.com/jobs")
        self.random_delay(2,4)
        kw = WebDriverWait(self.driver,10).until(
            EC.presence_of_element_located((By.XPATH,"//input[contains(@id,'jobs-search-box-keyword')]"))
        )
        kw.clear(); self.human_type(kw, JOB_TITLE)
        loc = self.driver.find_element(By.XPATH,"//input[contains(@id,'jobs-search-box-location')]")
        loc.clear(); self.human_type(loc, LOCATION)
        loc.send_keys(Keys.RETURN)
        self.random_delay(3,5)

    def apply_filters(self):
        try:
            self.random_scroll(); self.random_delay(1,2)
            WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((By.ID,'searchFilter_applyWithLinkedin'))
            ).click()
            self.random_delay(2,3)
            WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((By.ID,'searchFilter_timePostedRange'))
            ).click()
            self.random_delay(1,2)
            WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((By.XPATH,"//label[@for='timePostedRange-r86400'] | //span[contains(text(),'Past 24 hours')]") )
            ).click()
            self.random_delay(1,2)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,"//button[span[text()[contains(., 'Show') and contains(., 'results')]]]"))
            ).click()
            self.random_delay(2, 4)
            return True
        except Exception:
            return False
    def _dismiss_modal(self):
        try:
            cancel_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']"))
            )
            cancel_btn.click()
            self.random_delay(1, 2)
        except Exception:
            pass

    def submit_applications(self):
        applied = 0
        attempts = 0
        maxa = BATCH_SIZE * 3
        while applied < BATCH_SIZE and attempts < maxa:
            attempts += 1
            self.random_scroll(); self.random_delay(1,2)
            jobs = self.driver.find_elements(
                By.XPATH,
                "//button[@id='jobs-apply-button-id' and contains(normalize-space(.),'Easy Apply')]"
            )
            if not jobs:
                break
            for btn in jobs:
                if applied >= BATCH_SIZE:
                    break
                text = btn.text.strip()
                if 'Applied' in text:
                    continue
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    self.random_delay(1,2)
                    btn.click()
                    self.random_delay(2,3)
                    success = self._process_easy_apply_flow()
                    self._dismiss_modal()
                    if success:
                        applied += 1
                    else:
                        self._discard_application()
                    self.driver.back(); self.random_delay(3,5)
                except Exception:
                    continue
            if random.random() > 0.5:
                self.random_scroll(); self.random_delay(2,4)
        return applied

    def _process_easy_apply_flow(self):
        try:
            for _ in range(5):
                if self._is_application_complete():
                    return True
                if self._has_questions() and not self._answer_questions():
                    return False
                btns = {
                    'submit': self._find_submit_button(),
                    'review': self._find_review_button(),
                    'next': self._find_next_button()
                }
                clicked = False
                for t, b in btns.items():
                    if b and b.is_displayed():
                        b.click(); self.random_delay(2,3); clicked = True; break
                if not clicked:
                    return False
            return self._is_application_complete()
        except Exception:
            return False

    def _find_submit_button(self):
        try:
            return WebDriverWait(self.driver,5).until(
                EC.element_to_be_clickable((By.XPATH,"//button[contains(@aria-label,'Submit application') or contains(.,'Submit application')]") )
            )
        except:
            return None

    def _find_review_button(self):
        try:
            return WebDriverWait(self.driver,5).until(
                EC.element_to_be_clickable((By.XPATH,"//button[contains(@aria-label,'Review') or contains(.,'Review')]"))
            )
        except:
            return None

    def _find_next_button(self):
        try:
            return WebDriverWait(self.driver,5).until(
                EC.element_to_be_clickable((By.XPATH,"//button[contains(@aria-label,'Next') or contains(.,'Next')]") )
            )
        except:
            return None

    def _is_application_complete(self):
        try:
             self.driver.find_element(By.XPATH,
                "//*[contains(text(),'application submitted') or contains(text(),'application complete')]"
            )
        except:
            return False

    def _has_questions(self):
        try:
            return len(self.driver.find_elements(By.CSS_SELECTOR,'div.jobs-easy-apply-form-section__grouping')) > 0
        except:
            return False

    def _answer_questions(self):
        try:
            sections = self.driver.find_elements(By.CSS_SELECTOR,'div.jobs-easy-apply-form-section__grouping')
            for sec in sections:
                radios = sec.find_elements(By.XPATH, ".//input[@type='radio']")
                if radios:
                   # prefer “Yes” if available, else pick the first
                    for r in radios:
                        label = sec.find_element(By.TAG_NAME,'label').text.lower()
                        if 'yes' in r.get_attribute('value').lower():
                            r.click()
                            break
                    else:
                        radios[0].click()
                    continue

                # detect decimal/number inputs
                inputs = sec.find_elements(By.TAG_NAME, 'input')
                if inputs and 'decimal' in sec.text.lower() or 'experience' in sec.text.lower():
                # satisfying “decimal > 0.0” requirement
                    inp = inputs[0]
                    self.human_type(inp, '1.0')
                    continue
            for sec in sections:
                txt = sec.text.lower()
                if sec.find_elements(By.TAG_NAME,'select'):
                    self._handle_dropdown_question(sec, txt)
                elif 'salary' in txt:
                    self._handle_salary_question(sec)
                elif 'years' in txt:
                    self._handle_experience_question(sec)
                elif sec.find_elements(By.XPATH,".//input[@type='radio']"):
                    self._handle_radio_questions(sec)
                else:
                    self._handle_text_question(sec)
            return True
        except:
            return False

    def _handle_experience_question(self, el):
        try:
            sel = Select(el.find_element(By.TAG_NAME,'select'))
            for opt in ['2','3','4','5+']:
                try: sel.select_by_visible_text(opt); return True
                except: pass
            sel.select_by_index(1)
            return True
        except:
            return False

    def _handle_salary_question(self, el):
        try:
            inp = el.find_element(By.TAG_NAME,'input')
            self.human_type(inp, str(random.randint(60000,120000)))
            return True
        except:
            return False

    def _handle_radio_questions(self, el):
        try:
            radios = el.find_elements(By.XPATH,".//input[@type='radio']")
            if radios:
                random.choice(radios).click(); return True
            return False
        except:
            return False

    def _handle_dropdown_question(self, el, txt):
        try:
            sel = Select(el.find_element(By.TAG_NAME,'select'))
            if 'country' in txt:
                sel.select_by_visible_text('Pakistan')
            else:
                opts = [o.text for o in sel.options if 'Select' not in o.text]
                if opts: sel.select_by_visible_text(random.choice(opts))
            self.random_delay(0.5,1.5)
            return True
        except:
            return False

    def _handle_text_question(self, el):
        try:
            fld = el.find_element(By.TAG_NAME,'textarea') if el.find_elements(By.TAG_NAME,'textarea') else el.find_element(By.TAG_NAME,'input')
            lbl = el.find_element(By.TAG_NAME,'label').text.lower()
            ans = "Experienced software engineer with 5+ years..." if 'summary' in lbl else "I am excited to apply and meet the requirements."
            self.human_type(fld, ans)
            return True
        except:
            return False

    def _discard_application(self):
        try:
            btns = self.driver.find_elements(By.XPATH,"//button[contains(@aria-label,'Discard')] | //button[contains(.,'Discard')]")
            for b in btns:
                if b.is_displayed(): b.click(); self.random_delay(1,2); return True
            self.driver.find_element(By.TAG_NAME,'body').send_keys(Keys.ESCAPE)
            self.random_delay(1,2)
            return True
        except:
            return False

    def run(self, close_on_finish=True):
        self.setup_driver()
        try:
            if not self.login():
                return 0

            self.search_for_jobs()
            self.apply_filters()
        
            # wrap the per-job loop in its own guard
            try:
                return self.submit_applications()
            except Exception as job_e:
                print(f"Error in submit_applications: {job_e}")
                return 0

        except Exception as e:
            print(f"Fatal error: {e}")
            return 0

        finally:
        # only quit once all retries are done
            self.save_cookies()
            if close_on_finish:
                self.driver.quit()
            self._cleanup_proxy_files()


def load_accounts_from_csv(path):
    accounts = []
    try:
        with open(path) as f:
            for row in csv.DictReader(f):
                if row.get('email') and row.get('password'):
                    accounts.append({
                        'email': row['email'].strip(),
                        'password': row['password'].strip(),
                        'proxy': row.get('proxy','').strip() or random.choice(PROXY_LIST)
                    })
    except: pass
    return accounts


def run_bot_for_account(acc):
    bot = LinkedInBot(acc['email'], acc['password'], acc['proxy'])
    res = bot.run(close_on_finish=False); time.sleep(random.randint(10,30)); return res


def main():
    st.title("LinkedIn Job Application Bot")
    uploaded = st.file_uploader("Upload CSV of accounts", type='csv')
    if not uploaded: return
    temp = 'temp.csv'
    with open(temp,'wb') as f: f.write(uploaded.getbuffer())
    accounts = load_accounts_from_csv(temp)
    if not accounts: st.error("No valid accounts."); return
    st.write(f"Accounts: {len(accounts)}")
    if st.button("Start"):
        p = st.progress(0); status = st.empty(); results = []
        for i, acc in enumerate(accounts):
            status.text(f"{i+1}/{len(accounts)} - {acc['email']}")
            c = run_bot_for_account(acc)
            results.append({'email':acc['email'],'applied':c})
            p.progress((i+1)/len(accounts))
        st.write("## Results")
        for r in results: st.write(f"{r['email']}: {r['applied']} jobs")
        os.remove(temp)

if __name__=='__main__':
     main()