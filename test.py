import re
import dateparser
from datetime import datetime
from parsedatetime import parsedatetime as pdt

now = datetime.now()
print("now: %s" % now)

pattern = r"(\d+:\d+|\d+ [ap]m|tomorrow|today|yesterday|(this|next|last) (\d+ )?\w+|\d+ days? ago|\d+ days? later|\d+ weeks? ago|\d+ weeks? later|\d+ months? ago|\d+ months? later|\d+ years? ago|\d+ years? later)"

queries = ["When is my appointment tomorrow",
           "What do I have going on this week",
           "Whats going on the next 3 months",
           "How long ago was last year",
           "When will it be 2 years later",
           "What do I have going on this week?"]

for query in queries:
    print("Query: %s" % query)
    cal = pdt.Calendar()
    matches = cal.nlp(query_text)
    for match in matches:
        print("Found: %s" % match[0])
        parsed_time = dateparser.parse(match[0], settings={'RELATIVE_BASE': now})
        print("Parsed: %s" % parsed_time)
    print()