import time,requests,random,json,os,threading
from datetime import datetime, timedelta
from pystyle import Colorate, Colors, System, Write


good = [0]
dam = [0]
ratelimet = [0]


# main class
class Discord:
    def __init__(self, token, status):
        self.token = token
        self.status = status
        self.headers = {
            "Authorization": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "*/*"
        }
        self.rate_limit_reset = None

    def change_status(self, message, proxy=None):
        message_data = {
            "status": self.status,
            "custom_status": {
                "text": message
            }
        }
        if proxy:
            proxy_param = {
                'http': proxy,
                'https': proxy
            }
            response = requests.patch("https://discord.com/api/v8/users/@me/settings", headers=self.headers,
                                      json=message_data, proxies=proxy_param)
        else:
            response = requests.patch("https://discord.com/api/v8/users/@me/settings", headers=self.headers,
                                      json=message_data)
        if 'Retry-After' in response.headers:
            retry_after = int(response.headers['Retry-After'])
            self.rate_limit_reset = datetime.utcnow() + timedelta(seconds=retry_after)
        else:
            self.rate_limit_reset = None
        return response.status_code


def scrape_proxies(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        proxies = response.text.splitlines()
        return proxies
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while scraping proxies: {str(e)}")
        return []


def proxy_param(proxies):
    parsed_proxies = []
    for proxy in proxies:
        if isinstance(proxy, str):
            proxy_parts = proxy.split(":")
            if len(proxy_parts) == 2:
                # Format: IP:Port
                parsed_proxies.append({"http": f"http://{proxy_parts[0]}:{proxy_parts[1]}",
                                       "https": f"https://{proxy_parts[0]}:{proxy_parts[1]}"})
        elif isinstance(proxy, dict):
            # Format: Username:Password:IP:Port
            parsed_proxies.append(proxy)
    return parsed_proxies


def countdown(seconds):
    global ratelimet, dam, good
    try:
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            hours, mins = divmod(mins, 60)
            time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
            os.system(f"title Worked : [ {good[0]} ]   Failed : [ {dam[0]} ]  IP Blocked : [ {ratelimet[0]} ]  Time left: {time_str}")
            time.sleep(1)
            seconds -= 1
    except KeyboardInterrupt:
        os.system("title Countdown interrupted!")
        return
    os.system("title Countdown finished!")


def run_with_countdown(discord, used_messages, status, seconds):
    global ratelimet, dam, good
    with open('Data/messages.txt', 'r', encoding='utf-8') as message_file:
        all_messages = message_file.read().splitlines()

    available_messages = [message for message in all_messages if message not in used_messages]
    if not available_messages:
        print("No more available messages.")
        return

    message = random.choice(available_messages)
    used_messages.append(message)

    status_code = discord.change_status(message)
    if status_code == 200:
        good[0] += 1
        os.system("cls")
        print(Colorate.Horizontal(Colors.rainbow, f"""
                ╔═════ .♥.Pick Status .♥. ══════╗
                        Made By : pick666
                        Tiktok : pick
                    Instagram : _kingkillv6          
                        
                ╚═══════════════════════════════╝ 
                                                   ╔═════ .♥.Pick Status .♥. ══════╗
                                                         Worked : {good[0]}
                                                         Failed : {dam[0]}
                                                         Rate : {ratelimet[0]}
                                                   ╚═══════════════════════════════╝ 
                ╔═════ .♥.Pick Status .♥. ══════╗
                    Status : {message}

                    Time remaining: {timedelta(seconds=seconds)}

                ╚═══════════════════════════════╝ 
    """, 1))
    elif status_code == 429:
        ratelimet[0] += 1
        print(Colorate.Horizontal(Colors.red_to_white, f"[ Pick Status ] Error : Rate limited. Waiting for rate limit reset...",
                                  1))
        if discord.rate_limit_reset:
            now = datetime.utcnow()
            time_until_reset = discord.rate_limit_reset - now
            sleep_time = time_until_reset.total_seconds() + 1
            print(Colorate.Horizontal(Colors.red_to_white, f"[ Pick Status ] Error : Rate limit reset. Retrying... {sleep_time}", 1))
            time.sleep(sleep_time)  # Sleep for the reset time
            run_with_countdown(discord, used_messages, status, seconds)
        else:
            print(Colorate.Horizontal(Colors.red_to_white,
                                      f"[ Pick Status ] Error : Unable to determine rate limit reset time. Please try again later.",
                                      1))
    else:
        dam[0] += 1
        print("")


def main():
    with open('input/config.json', 'r') as config_file:
        config = json.load(config_file)

    token = config['token']
    sleep_time = config['sleep_time']
    status = config['status']
    use_custom_proxies = config.get('use_custom_proxies', False)
    proxy_api_url = config.get('proxy_api_url',
                               'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=1000&country=all&ssl=all&anonymity=all')

    used_messages = []
    discord = Discord(token, status)

    proxies = []
    if use_custom_proxies:
        proxies = proxy_param(config.get('proxies', []))
    elif proxy_api_url:
        proxies = proxy_param(scrape_proxies(proxy_api_url))

    while True:
        seconds = sleep_time
        countdown_thread = threading.Thread(target=countdown, args=(seconds,))
        countdown_thread.start()

        run_with_countdown(discord, used_messages, status, seconds)

        countdown_thread.join()
        used_messages.clear()


if __name__ == '__main__':
    main()
