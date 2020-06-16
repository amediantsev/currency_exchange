from django import forms

from account.models import Comment


class CommentForm(forms.ModelForm):
    author = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    source = forms.IntegerField(
        widget=forms.HiddenInput()
    )
    text = forms.CharField(
        label='Comment',
        widget=forms.TextInput(
            attrs={
                'class': 'd33__input',
                'placeholder': 'Leave your comment here...',
            },
        )
    )

    class Meta:
        model = Comment
        fields = ['text', ]
