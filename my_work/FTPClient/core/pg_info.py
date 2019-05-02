
def progress(percent,width=50):
    if percent >= 1:
        percent=1
    show_str = ('%%-%ds' % width) % (int(width*percent)*'*')
    print('\r%s %d%%' %(show_str, int(100*percent)), end='')