from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django import template
 
register = template.Library()
 
@register.filter
@stringfilter
def zerowidthspace_separator(value, num):
  """
  Add zero-width space every num chars in string
  """
  num = int(num)
  locations = range(0, len(value), num)[1:] # loc to insert
   
  new_value = value[:num]
   
  for loc in locations:
    if loc + num < len(value):
      new_value += '​' + value[loc:(loc+num)]
    else:
     new_value += '​' + value[loc:] # last substring may have less than num chars
     
  return mark_safe(new_value)
