CURR_USD, CURR_EUR = range(1, 3)
SR_PRIVAT, SR_MONO,\
SR_VKURSE, SR_OTP, \
SR_PUMB, SR_OSHCHAD = range(1, 7)


CURRENCY_CHOICES = (
    (CURR_USD, 'USD'),
    (CURR_EUR, 'EUR'),
)

SOURCE_CHOICES = (
    (SR_PRIVAT, 'PrivatBank'),
    (SR_MONO, 'MonoBank'),
    (SR_VKURSE, 'Vkurse'),
    (SR_OTP, 'Otp'),
    (SR_PUMB, 'Pumb'),
    (SR_OSHCHAD, 'Oshchad')
)
