from ics import Calendar, Event
import arrow

class Schedule:
  def __init__(self):
    self.calendar = Calendar()


  def addShift(self, begin, end, role, store, meal_time, hours):
    try:
      name = f"Publix {role} Shift"
      description = f"{role} Shift\n{store}\nMeal: {meal_time}\nHours: {hours}\n\nGenerated by PubSub (https://github.com/andrewmartyn/pubsub)"
      shift = Event(
        name=name, 
        begin=begin, 
        end=end, 
        description=description, 
        location=store, 
        organizer="publix.org")
      self.calendar.events.add(shift)
    except Exception as e:
      print(e)
    
    return shift
  
  def parseTime(self, time):
    try:
      a, b = time.split(' ')
      if len(a.split(':')) > 1: 
        hour, minute = [int(x) for x in a.split(':')]
      else:
        hour = int(a)
        minute = 0

      if b == 'p.m.':
        hour += 12
    except Exception as e:
      print(e)
    
    return hour, minute
  
  
  def addShifts(self, shifts):
    try:
      if len(shifts) > 0:
        for shift in shifts:
          date, store, role, shift_time, meal_time, hours = shift

          start, end = shift_time.split(' - ')
          start_time_hour, start_time_minute = self.parseTime(start)
          end_time_hour, end_time_minute = self.parseTime(end)
          month, day, year = [int(x) for x in date.split('/')]

          begin = arrow.Arrow(year=year, month=month, day=day, hour=start_time_hour, minute=start_time_minute, tzinfo="America/New_York")
          end = arrow.Arrow(year=year, month=month, day=day, hour=end_time_hour, minute=end_time_minute, tzinfo="America/New_York")

          self.addShift(begin, end, role, store, meal_time, hours)
    except Exception as e:
      print(e)


  def export(self, file_name):
    if len(self.calendar.events) > 0:
      with open(f"{file_name}", 'w') as f:
        f.writelines(self.calendar.serialize_iter())
    else:
      print("There's nothing to export... (Something likely went wrong)")

