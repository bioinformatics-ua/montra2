from fingerprint.models import Answer

answers = Answer.objects.filter(question__slug_fk__slug1='Publications')

for answer in answers:
    answer.data = answer.data.replace('heimer"s', "heimer's")
    answer.save()
