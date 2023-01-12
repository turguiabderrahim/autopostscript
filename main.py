import pyautogui
import time
import webbrowser


groups="https://www.facebook.com/groups/646279699717178"
webbrowser.register('chrome',None,webbrowser.BackgroundBrowser('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'))
pyautogui.hotkey('ctrl','t')
webbrowser.get('chrome').open_new(groups)
time.sleep(20)
pyautogui.hotkey('ctrl','f')
pyautogui.typewrite("Write something...")
pyautogui.press('enter')
pyautogui.press('escape')
pyautogui.press('enter')
time.sleep(3)
pyautogui.hotkey('ctrl','v')
time.sleep(3)
pyautogui.typewrite('#fg')
pyautogui.hotkey('ctrl','f')
time.sleep(3)
pyautogui.typewrite("Post")
pyautogui.press('enter')
pyautogui.press('escape')
pyautogui.press('enter')
time.sleep(6)
pyautogui.hotkey('ctrl','w')
