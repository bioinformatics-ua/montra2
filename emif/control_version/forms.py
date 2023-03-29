from django import forms


class BugReportForm(forms.Form):
    NOP = 'Not really a problem'
    LOW = 'Low Priority'
    MED = 'Medium Priority'
    HIGH = 'High Priority'
    CRIT = 'Critical Priority'
    PRIORITIES = (
        (LOW, 'Low Priority'),
        (MED, 'Medium Priority'),
        (HIGH, 'High Priority'),
        (CRIT, 'Critical Priority'),
        (NOP, 'Not really a problem'),

    )
    title = forms.CharField(label='Title', widget=forms.TextInput(attrs={'class': 'span6', 'placeholder': 'Title'}))
    description = forms.CharField(
        label='Description',
        initial='',
        widget=forms.Textarea(attrs={'cols': 30, 'rows': 8, 'class': 'span6', 'placeholder': 'Description'}),
    )

    '''steps = forms.CharField(label='Steps to reproduce', initial='',
        widget=forms.Textarea(attrs={'cols': 30, 'rows': 4, 'class': 'span6', 'placeholder': 'Steps to reproduce'}))

    expected = forms.CharField(label='Expected Result', initial='',
        widget=forms.Textarea(attrs={'cols': 30, 'rows': 4, 'class': 'span6', 'placeholder': 'Expected Result'}))

    priority = forms.ChoiceField(label='Priority', choices=PRIORITIES,
        widget=forms.Select(attrs={'class': 'span6', 'placeholder': 'Priority'}))
    '''
