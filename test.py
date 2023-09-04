import time


def formatDate():
    S = int(time.time()) - 1693783816
    result = ''
    days = S // 86400
    S = S % 86400
    if days != 0 and days != 1:
        result = f'{days} days ' #writes the seconds only when the value is neither 0 or 1
    elif days == 1:
        result = f'{days} day ' #remove the 's' when the value is 1

    hours = S // 3600
    S = S % 3600
    if hours != 0 and hours != 1:
        result += f'{hours} hours '
    elif hours == 1:
        result += f'{hours} hour '
    minutes = S // 60
    S = S % 60
    if minutes != 0 and minutes != 1:
        result += f'{minutes} minutes '
    elif minutes == 1:
        result += f'{minutes} minute'
    if S != 0 and S != 1:
        result += f'{S} seconds'
    elif S == 1:
        result += f'{S} second'
    return result

print(formatDate())