import mechanize

# create a new browser
browser = mechanize.Browser()

# # set the cookie jar
# browser.set_cookiejar(cookie_jar)

# # create a new cookie
# cookie = mechanize.Cookie(
#     version=0,
#     name='.ASPXAUTH',
#     value='68E5CE595087E9079222445F55465E5B8E0B971348155E2B20CE3EBF6DD1A5FFDCA1185B15547E699B368EF9791E5286308CAF2D3441883CF451F6394A2CAE55EC060A3002A4A8AECD57C8EC49176FC17416A6B6CEA99C0B01EF53583C40AA347E61E4F5946871AA9C05E959AAA5744EDF4804981483F54701DA1F5ACB678FB18808421FA243B8D0575B96C33A12AF8336B6DAFFF7565737241C67CF7DCAF8B582EE1B34741F0CECAB1956D984BD0CC88C27D3F8817C245A5D47BFB3173A22AEDF9F8396CDB759985F007CB2417C468F90BE0A13A18EB8216586F7B20F6FEB9666525C2A',
#     port=None,
#     port_specified=False,
#     domain='bot.solesbot.ai',
#     domain_initial_dot=False,
#     domain_specified=True,
#     path='/',
#     path_specified=True,
#     secure=False,
#     expires=None,
#     discard=True,
#     comment=None,
#     comment_url=None,
#     rest={'HttpOnly': None},
#     rfc2109=False
# )

# # add the cookie to the jar
# cookie_jar.set_cookie(cookie)

# set the user agent
browser.addheaders = [
    (
        "User-agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    )
]

# get the HTML content of the page
page = browser.open("https://bot.solesbot.ai/dashboard")

# select the form
browser.select_form(nr=0)
browser.form.set_all_readonly(False)
# fill in the form fields
# browser.form["wallet"] = "usdt"
# browser.form["amount"] = "0,566213"
# browser.form["fromWalletvl"] = "spot"
# browser.form["toWalletvl"] = "arbitrage"
browser.form["Email"] = "arias.eliann@gmail.com"
browser.form["Password"] = "junpuc-tuzXav-kuvmy2"

# submit the form
response = browser.submit()

# print the response
print(browser.cookiejar._cookies["bot.solesbot.ai"]["/"][".ASPXAUTH"].value)


# # URL of the form
# session = BotSession("68E5CE595087E9079222445F55465E5B8E0B971348155E2B20CE3EBF6DD1A5FFDCA1185B15547E699B368EF9791E5286308CAF2D3441883CF451F6394A2CAE55EC060A3002A4A8AECD57C8EC49176FC17416A6B6CEA99C0B01EF53583C40AA347E61E4F5946871AA9C05E959AAA5744EDF4804981483F54701DA1F5ACB678FB18808421FA243B8D0575B96C33A12AF8336B6DAFFF7565737241C67CF7DCAF8B582EE1B34741F0CECAB1956D984BD0CC88C27D3F8817C245A5D47BFB3173A22AEDF9F8396CDB759985F007CB2417C468F90BE0A13A18EB8216586F7B20F6FEB9666525C2A")
# bot_session = session.bot_session()
# url = "https://bot.solesbot.ai/wallet/transfer"

# # HTML content of the page
# html_content = bot_session.get(url).text

# # Parse the HTML content using BeautifulSoup
# soup = BeautifulSoup(html_content, "html.parser")

# # Find the form element
# form = soup.find("form", method="post")

# # Extract the form fields
# fields = {}
# # for input_field in form.find_all("input"):
# #     name = input_field.get("name")
# #     value = input_field.get("value", "")
# #     fields[name] = value

# # Modify the form fields as needed
# fields["wallet"] = "usdt"
# fields["amount"] = "0.67"
# fields["fromWalletvl"] = "spot"
# fields["toWalletvl"] = "arbitrage"

# # Submit the form
# response = bot_session.post(url, data=fields)

# # Check the response
# if response.status_code == 200:
#     print("Form submitted successfully!")
# else:
#     print(f"Error submitting form: {response.status_code}")
