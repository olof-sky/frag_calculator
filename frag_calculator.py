import datefinder, os
from datetime import date, datetime, timedelta
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def render_index():
    return render_template('index.html')
    
@app.route('/art')
def render_art():
    return render_template('art.html')
    
@app.route('/support')
def render_support():
    return render_template('support.html')
    
@app.route('/submit_frags', methods=['POST'])
def submit_frags():
    frag_list = request.form.get('kills')
    frag_split = frag_list.split('\t')
    list_of_frag_lists = [frag_split[x:x+6] for x in range(1, len(frag_split), 6)]
    result = []
    return render_template('submit_frags.html', result = (unjust_status(timediff(dates(unjusts(list_of_frag_lists))))))
    
def unjusts(frag_unjusts):
    frag_list = frag_unjusts
    just = ['justified']
    for item in range(len(frag_list) - 1, -1, -1):
        for x in just:
            if x in frag_list[item]:
                del frag_list[item]
    return str(frag_unjusts)

def dates(dates):
    input_string = dates
    dates_list = list(datefinder.find_dates(input_string))
    return (dates_list)

def timediff(dates_list):
    todays_date = datetime.today()
    time_diff = []
    for item in dates_list:
        time_diff.append(todays_date.replace(tzinfo = None) - item.replace(tzinfo = None))
    return [time_diff, dates_list]

def remove_old_frags(frag_list):
    dates_list = []
    for date in frag_list:
        if (datetime.today().replace(tzinfo = None) - date.replace(tzinfo = None)).total_seconds() < 2592000:
            dates_list.append(date)
            dates_list = sorted(dates_list, reverse = True)
    return(dates_list)

def count_number_of_unjusts(frag_list):
    day_unjust = 0
    week_unjust = 0
    month_unjust = 0
    for item in frag_list:
        if item < timedelta(days = 1, minutes = 0, seconds = 0):
            day_unjust += 1
        if item < timedelta(days = 7, minutes = 0, seconds = 0):
            week_unjust += 1
        if item < timedelta(days = 30, minutes = 0, seconds = 0):
            month_unjust += 1
    return({
        "day": day_unjust,
        "week": week_unjust,
        "month": month_unjust
    })

def check_weekly_span(dates_list):
    status = {
        "redskull": False,
        "ban": False
    }
    bans = []
    actually_banned = False
    for delta in dates_list:
        counter = 0
        for delta2 in dates_list:
            if (max([delta2, delta]) - min([delta2, delta])).total_seconds() < 604800:
                counter = counter + 1
            if counter > 5:
                status["redskull"] = True
            if counter > 10:
                status["ban"] = True
                bans.append(delta)
    for ban_time in bans:
        if (datetime.today().replace(tzinfo = None) - ban_time.replace(tzinfo = None)).total_seconds() < 604800:
            actually_banned = True
    if status["ban"] and actually_banned:
        status["ban"] = True
    else:
        status["ban"] = False
    return(status)

def check_daily_span(dates_list):
    status = {
        "redskull": False,
        "ban": False
    }
    bans = []
    actually_banned = False
    for delta in dates_list:
        counter = 0
        for delta2 in dates_list:
            if (max([delta2, delta]) - min([delta2, delta])).total_seconds() < 86400:
                counter = counter + 1
            if counter > 2:
                status["redskull"] = True
            if counter > 5:
                status["ban"] = True
                bans.append(delta)
    for ban_time in bans:
        if (datetime.today().replace(tzinfo = None) - ban_time.replace(tzinfo = None)).total_seconds() < 604800:
            actually_banned = True
    if status["ban"] and actually_banned:
        status["ban"] = True
    else:
        status["ban"] = False
    return(status)

def i_am_banned(frag_list_input):
    ban_left = []
    ban_output = []
    latest_unjust = datetime(1900, 1, 1)
    for item in remove_old_frags(frag_list_input[1]):
        if latest_unjust.replace(tzinfo = None) < item.replace(tzinfo = None):
            latest_unjust = item
        ban_left = datetime.today().replace(tzinfo = None) - (latest_unjust).replace(tzinfo = None)
        ban_output = timedelta(days = 7, minutes = 0, seconds = 0) - ban_left
        days = ban_output.days
        seconds = ban_output.seconds
        hours = seconds//3600
        minutes = (seconds//60%60)
    return ("","","","You are banned", "DAYS",(days), "HOURS",(hours), "MINUTES",(minutes), " left until ban lift")
    
def i_am_redskull(frag_list_input):
    frag_counts = count_number_of_unjusts(frag_list_input[0])
    day_frags_left = 5 - frag_counts["day"]
    week_frags_left = 9 - frag_counts["week"]
    month_frags_left = 19 - frag_counts["month"]
    ban_list = min(day_frags_left, week_frags_left, month_frags_left)
    return ("You're redskull, you have",(ban_list), "safe frag(s) until ban")

def i_am_pure(frag_list_input):
    redskull_list =[]
    frag_counts = count_number_of_unjusts(frag_list_input[0])
    if frag_counts["day"] >= 0 or frag_counts["week"] >= 0 or frag_counts["month"] >= 0:
        day_frags_left = 2 - frag_counts["day"]
        week_frags_left = 4 - frag_counts["week"]
        month_frags_left = 9 - frag_counts["month"]
        redskull_list = min(day_frags_left, week_frags_left, month_frags_left)
    return ("You have",(redskull_list), "safe frag(s)")

def unjust_status(frag_list_input):
    already_redskull = False
    if check_weekly_span(remove_old_frags(frag_list_input[1]))["redskull"]\
        or check_daily_span(remove_old_frags(frag_list_input[1]))["redskull"]:
            already_redskull = True

    already_banned = False
    if check_weekly_span(remove_old_frags(frag_list_input[1]))["ban"]\
        or check_daily_span(remove_old_frags(frag_list_input[1]))["ban"]:
            already_banned = True

    if already_banned:
        return i_am_banned(frag_list_input)
    if already_redskull:
        return i_am_redskull(frag_list_input)
    return i_am_pure(frag_list_input)
