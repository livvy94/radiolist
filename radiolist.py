import os
import webbrowser
import calendar
from datetime import datetime
from enum import Enum
from itertools import chain
import clipboard #if this isn't working, run "pip install clipboard"
from secrets import frequency, callsign, second_channel, weather_link

#TODO: Make a rudimentary time-tracker?
#TODO: Display of current killdates for Next Friday, Saturday, & Sunday

def main():
    open_urls = True
    mode = Mode.LISTFILLS #start off at the fills view 'cause I usually do those first

    #TODO: find out if you can move these further down so the appends are the first thing you see
    #This is stuff laying out the structure of how fill and promo notation works
    class fill:
        def __init__(self, time, cut_number, secs, optional_specific_underwriting = "", optional_currently_playing_program = "(None)"):
            self.time = time
            self.cut_number = cut_number
            self.secs = secs
            self.optional_specific_underwriting = optional_specific_underwriting
            self.optional_currently_playing_program = optional_currently_playing_program
            self.done = False
        def __str__(self):
            result = get_done_status(self)
            
            result += f"{self.time.rjust(5, ' ')}".ljust(8, ' ')
            result += f"{self.cut_number}".ljust(8, ' ')
            result += f"{format_seconds(self.secs)}".ljust(10, ' ')
            if self.optional_specific_underwriting:
                result += f"LIVE: {self.optional_specific_underwriting}"
            return result


    class promo:
        def __init__(self, day_available, cut_number, show_name, announcement_text, url):
            self.day_available = day_available
            self.cut_number = cut_number
            self.show_name = show_name
            self.announcement_text = announcement_text #the thing to record at the end
            self.url = url
            self.done = False
        def __str__(self):
            result = get_done_status(self)
            result += f"{self.cut_number}  {self.show_name}"
            return result

    fills = [
        #fill("7:29", "50598",  30,  "L#178 Krasl", "This American Life"),
        #fill("7:59", "50083",  30,  ""),
        
        #fill("8:06", "50599",  0),
        #fill("8:20", "50600",  10,  "", "q from the CBC"),
        #fill("8:40", "50601",  0,  "", "q from the CBC"),
        #fill("8:59", "50172",  30),
        
        #fill("9:06", "52403",  10),
        #fill("9:20", "52404",  10,  "", "The Middle with Jeremy Hobson"),
        #fill("9:39", "52405",  30, "", "The Middle with Jeremy Hobson"),
        #fill("9:59", "52105",  10, ""),
        
        #fill("10:21","52106", 50,  "", "Think"),
        #fill("10:41","52107", 20,  "Coming up is the rest of Think followed by the BBC @ 11", "Think"),
        #fill("10:59","50086", 10),
        
        #fill("11:59","52110", 30,  "", "BBC World Service"),
        
        #fill("12:59","50193", 10, "", "BBC World Service"),
        #fill("1:59", "50194", 10, "", "BBC World Service"),
        #fill("2:59", "50195", 20, "", "BBC World Service"),
        #fill("3:59", "50196", 20, "", "BBC World Service"),
        #fill("4:59", "50197", 20, "", "Coming up next is Morning Edition"),
    ]
    
    days = build_days() # Make a list of all of the days of the week
    
    MondayWeeklyPromos = [
        promo("Monday", "00012", "The Moth Radio Hour", f"Fridays at 7 PM and Saturdays at Noon here on {frequency} {callsign}", "https://exchange.prx.org/series/32832-the-moth-radio-hour"),
        promo("Monday", "00017", "City Arts & Lectures (latest episode -> promos)", f"Saturdays at 5 AM here on {frequency} {callsign}", "https://contentdepot.prss.org/portal/media/programs/7643"),
        promo("Monday", "00019", "Big Picture Science", f"Tuesdays at 7 PM and Sundays at 7 AM here on {frequency} {callsign}", "https://contentdepot.prss.org/portal/media/programs/927172"),
        promo("Monday", "00020", "The Splendid Table", f"Sunday mornings at 10 here on {frequency} {callsign}", "https://contentdepot.prss.org/portal/media/programs/496944"),
        promo("Monday", "00034", "Hidden Brain (use special tag!)", f"Sundays at 4 PM here on {frequency} {callsign}", "https://contentdepot.prss.org/portal/media/programs/4881964"),
        promo("Monday", "00079", "Mountain Stage", f"Sundays from 11 AM to 1 PM here on {frequency} {callsign}", "https://contentdepot.prss.org/portal/media/programs/496531"),
        promo("Monday", "00040", "Radiolab", f"Saturdays at 3 PM on {callsign} {second_channel}", "https://contentdepot.prss.org/portalui2/program/details?programId=3974426"),
        promo("Monday", "00044", "Travel with Rick Steves", f"Saturdays at Noon on {callsign} {second_channel}", "https://contentdepot.prss.org/portalui2/program/details?programId=4960806"),
    ]
    
    TuesdayWeeklyPromos = [
        promo("Tuesday", "00015", "The New Yorker Radio Hour", f"Saturday mornings at 11 here on {frequency} {callsign}", "https://contentdepot.prss.org/portal/media/programs/3985238"),
        promo("Tuesday", "00035", "The Ted Radio Hour", f"Saturdays at 6 AM here on {frequency} {callsign}", "https://contentdepot.prss.org/portal/media/programs/1149598"),
        promo("Tuesday", "00038", "A Way With Words", f"Sundays at 5 AM here on {frequency} {callsign}", "https://contentdepot.prss.org/portal/media/programs/917382"),
        promo("Tuesday", "00059", "Bullseye", f"Sundays at 2 PM on {callsign} {second_channel}", "https://contentdepot.prss.org/portalui2/program/details?programId=1390714"),
    ]
    
    WednesdayWeeklyPromos = [
        promo("Wednesday", "00037", "Wait Wait... Don't Tell Me!", f"Saturday mornings at 10 here on {frequency} {callsign}", "https://contentdepot.prss.org/portal/media/programs/496269"),
        promo("Wednesday", "00063", "Living on Earth", f"Sunday mornings at 6 o'clock here on {frequency} {callsign}", "https://exchange.prx.org/series/38401-living-on-earth"),
        promo("Wednesday", "00011", "It's Been A Minute", f"Saturday evenings at 5 on {callsign} {second_channel}", "https://contentdepot.prss.org/portalui2/program/details?programId=4931164"),
        promo("Wednesday", "00054", "Planet Money/How I Built This", f"Saturday mornings at 9 on {callsign} {second_channel}", "https://contentdepot.prss.org/portalui2/program/details?programId=4710724"),
    ]
    
    ThursdayWeeklyPromos = [
        promo("Thursday", "00013", "Weekend Edition Saturday", f"Saturdays from 8 to 10 AM on {frequency} {callsign} and from 10 AM to 12 PM on {second_channel}", "https://contentdepot.prss.org/portal/media/programs/142574"),
        promo("Thursday", "00016", "On The Media", f"Saturdays at 7 AM on {frequency} {callsign}", "https://contentdepot.prss.org/portal/media/programs/3974648"),
        promo("Thursday", "00025", "This American Life", f"Saturdays at 4 PM and Wednesdays at 7 PM on {frequency} {callsign}", "https://exchange.prx.org/series/33783-this-american-life"),
        promo("Thursday", "00077", "Fresh Air Weekend", f"Sundays at 1 PM on {callsign} {second_channel}", "https://contentdepot.prss.org/portalui2/program/details?programId=496580"),
        promo("Thursday", "00081", "eTown", f"Sundays at 11 PM on {callsign} {second_channel}", "https://contentdepot.prss.org/portalui2/program/details?programId=938964"),
    ]
    
    FridayWeeklyPromos = [
        promo("Friday", "00045", "Reveal", f"Thursdays at 7 PM here on {frequency} {callsign}", "https://exchange.prx.org/series/34599-reveal-weekly"),
        promo("Friday", "00010", "Weekend Edition Sunday", f"Sunday at 8-10 AM on {frequency} {callsign} and from 10 AM to 12 PM on {second_channel}", "https://contentdepot.prss.org/portal/media/programs/142576"),
        promo("Friday", "00014", "ATC Weekend (Saturday)", f"Saturday evenings at 5 on {frequency} {callsign} and at 6 PM on {second_channel}", "https://contentdepot.prss.org/portal/media/programs/142578"),
        promo("Friday", "00051", "ATC Weekend (Sunday)", f"Sunday evenings at 5 on {frequency} {callsign} and at 6 PM on {second_channel}", "https://contentdepot.prss.org/portal/media/programs/142578"),
        promo("Friday", "00052", "Freakonomics Radio", f"Saturdays at 2 PM on {callsign} {second_channel}", "https://contentdepot.prss.org/portal/media/programs/3975096"),
        promo("Friday", "00073", "Day 6", f"Sundays at Noon on {callsign} {second_channel}", "https://exchange.prx.org/series/38397-day-6"),
    ]
    
    
    Dailies = [
        promo(get_today(days), "00001", "Morning Edition", f"Weekdays from 5 to 10 AM on {frequency} {callsign}", "https://contentdepot.prss.org/portalui2/program/details?programId=142565"),
        promo(get_today(days), "00003", "1A (Hour 1)", f"Weekdays at 10 AM on {frequency} {callsign}, and later at 4 PM on {callsign} {second_channel}", "https://contentdepot.prss.org/portalui2/program/details?programId=4175430"),
        promo(get_today(days), "00032", "1A (Hour 2)", f"Weekdays from 10 AM to Noon on {callsign}, 4-6 PM {second_channel}", ""),
        promo(get_today(days), "00004", "Here & Now (Hour 1)", f"Weekdays at Noon on {frequency} {callsign}, and 2 PM on {callsign} {second_channel}", "https://contentdepot.prss.org/portal/media/programs/1503574"),
        promo(get_today(days), "00005", "Here & Now (Hour 2)", f"Weekdays from 12 to 2PM on {frequency} {callsign}, and from 2 to 4 PM on {second_channel}", ""),
        promo(get_today(days), "00006", "Fresh Air", f"2 PM on {frequency} {callsign} & 9 PM on {callsign} {second_channel}", "https://contentdepot.prss.org/portal/media/programs/496578"),
    ]
    
    DailiesForFriday = [
        promo(get_today(days), "00001", "Morning Edition", f"Weekdays from 5 to 10 AM on {frequency} {callsign}", "https://contentdepot.prss.org/portalui2/program/details?programId=142565"),
        promo(get_today(days), "00003", "1A (Hour 1)", f"Weekdays at 10 AM on {frequency} {callsign}, and later at 4 PM on {callsign} {second_channel}", "https://contentdepot.prss.org/portalui2/program/details?programId=4175430"),
        promo(get_today(days), "00032", "1A (Hour 2)", f"Weekdays from 10 AM to Noon on {callsign}, 4-6 PM {second_channel}", ""),
        promo(get_today(days), "00004", "Here & Now (Hour 1)", f"Weekdays at Noon on {frequency} {callsign}, and 2 PM on {callsign} {second_channel}", "https://contentdepot.prss.org/portal/media/programs/1503574"),
        promo(get_today(days), "00005", "Here & Now (Hour 2)", f"Weekdays from 12 to 2PM on {frequency} {callsign}, and from 2 to 4 PM on {second_channel}", ""),
        promo(get_today(days), "00006", "Science Friday", f"2 PM on {frequency} {callsign} & Saturday night at 7 on {second_channel}", "https://contentdepot.prss.org/portal/media/programs/5253044"),
    ]

    # Add everything into one big collection
    temp = []
    if get_today(days) != "FRIDAY":
        temp = [MondayWeeklyPromos, TuesdayWeeklyPromos, WednesdayWeeklyPromos, ThursdayWeeklyPromos, FridayWeeklyPromos, Dailies]
    else:
        temp = [MondayWeeklyPromos, TuesdayWeeklyPromos, WednesdayWeeklyPromos, ThursdayWeeklyPromos, FridayWeeklyPromos, DailiesForFriday]
    
    promos = list(chain(*temp))
    
    while(True): #loop forever. exit by hitting Ctrl+C
        clear()
        #########################################################
        if mode == Mode.LISTFILLS:
            if len(fills) == 0:
                print("🎀 No fills today!")
            else:
                print ("   *** FILLS ***")
                for fill in fills:
                    print(fill)
            print()
                
            #prompt the user
            print("G: Go!                    L: Sort by length")
            print("M: Switch to Promo Mode   W: Launch weather.gov")
            userinput = input().upper()
            
            if userinput == "L": #length
                fills.sort(key=lambda x: x.secs) #heh
            elif userinput == "G": #go!
                mode = Mode.DOFILL
            elif userinput == "M": #switch modes
                mode = Mode.LISTPROMOS
            elif userinput == "W": #launch the weather site
                open_url(weather_link)
            elif userinput == "C" or userinput == "Q":
                exit()
        #########################################################
        elif mode == Mode.DOFILL:
            for fill in fills:
                if fill.done:
                    continue #skip ones marked as DONE!
                
                copy_cut_number(fill)

                clear()
                print(f" TIME   CUT #".ljust(35, ' ') + "CURRENT SHOW")
                print(f"{fill.time.rjust(5, ' ').ljust(8, ' ')}{fill.cut_number} ~ {format_seconds(fill.secs)}".ljust(35, ' ') + fill.optional_currently_playing_program)
                if fill.optional_specific_underwriting:
                    print(f" LIVE READ: {fill.optional_specific_underwriting}")
                print()
                
                #prompt the user
                print("D: Mark as DONE")
                print("S: Skip for now")
                print("R: Return to list")
                userinput = input().upper()
                
                if userinput == "D":
                    fill.done = True
                elif userinput == "S":
                    print(f"Skipping {fill.cut_number}...")
                elif userinput == "R":
                    break
            
            mode = Mode.LISTFILLS #Go back to the list view so the user can see which ones they skipped
        #########################################################
        elif mode == Mode.LISTPROMOS:
            # days = build_days() #This is now on line 140
            print (f"   *** PROMOS FOR {get_today(days)} ***")
                
            for promo in promos:
                if not_today(promo.day_available, days):
                    continue
                print(promo)
        
            #prompt the user
            print()
            print("G: Go!")

            if open_urls:
                print("U: Disable URL launching")
            else:
                print("U: Enable URL launching")

            print("M: Switch to Fill Mode")
            userinput = input().upper()
            
            if userinput == "G": # go!
                mode = Mode.DOPROMO
            elif userinput == "M": #switch modes
                mode = Mode.LISTFILLS
            elif userinput == "U":
                open_urls = not open_urls #if it's true, set it to false; vice versa
            elif userinput == "C" or userinput == "Q":
                exit()
        #########################################################        
        elif mode == Mode.DOPROMO:
            for promo in promos:
                if not_today(promo.day_available, days):
                    continue
                elif promo.done:
                    continue
                
                copy_cut_number(promo)
                
                clear()
                print(f"{promo.show_name} - {promo.cut_number}")
                print(promo.announcement_text)
                
                #prompt the user
                print("D: Mark as DONE")
                print("S: Skip for now")
                print("R: Return to list")
                if open_urls:
                    open_url(promo.url)
                userinput = input().upper()
                
                if userinput == "D": #TODO: hmm this seems like it could be consolidated
                    promo.done = True
                elif userinput == "S":
                    print(f"Skipping {promo.cut_number}...")
                elif userinput == "R":
                    break
                    
            mode = Mode.LISTPROMOS
            
###############################################################################
# Helper methods & doodads

def build_days():
    return dict(enumerate(calendar.day_name)) #build a list of days (0: 'Monday', 1: 'Tuesday', etc.)

def open_url(url):
    if (url != ""):
        webbrowser.open(url, new=0, autoraise=True)

def clear():
    os.system('clear') #this version works on the Windows Linux Subsystem (Currently I use the Ubuntu one though I normally use Debian)
    # os.system('cls') #this version works on Windows (untested)

def get_done_status(thing): #these next two methods work on both fills and promos!
    if thing.done == False:
        return "🔥 "
    else:
        return "✅ "

def format_seconds(seconds):
    if seconds != 0:
        return f"{seconds} secs"
    else:
        return "ZERO OUT" #for fills that *are* filled with prerecorded underwriting or spots already!

def copy_cut_number(thing):
    clipboard.copy(thing.cut_number)

def not_today(day_promo_is_available, days):
    return day_promo_is_available.upper() != get_today(days)

def get_today(days):
    return days[datetime.today().weekday()].upper()

class Mode(Enum):
    LISTFILLS = 0
    DOFILL = 1
    LISTPROMOS = 2
    DOPROMO = 3


#now that everything is defined, run the dang thing
if __name__ == "__main__":
    main()