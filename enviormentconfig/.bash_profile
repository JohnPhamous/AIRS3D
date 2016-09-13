# Visual settings

orange=$(tput setaf 166);
yellow=$(tput setaf 228);
green=$(tput setaf 71);
white=$(tput setaf 15);
blue=$(tput setaf 34);
bold=$(tput bold);
reset=$(tput sgr0);

PS1="\[${bold}\]\W";
PS1+="\[${white}\]\: \[${reset}\]";
export PSI;

# Setting PATH for Python 3.5
# The orginal version is saved in .bash_profile.pysave
PATH="/Library/Frameworks/Python.framework/Versions/3.5/bin:${PATH}"
export PATH

# Setting PATH for Python 3.5
# The orginal version is saved in .bash_profile.pysave
PATH="/Library/Frameworks/Python.framework/Versions/3.5/bin:${PATH}"
export PATH

# Setting PATH for Python 3.5
# The orginal version is saved in .bash_profile.pysave
PATH="/Library/Frameworks/Python.framework/Versions/3.5/bin:${PATH}"

# Setting PATH for Python 3.4
# The orginal version is saved in .bash_profile.pysave
PATH="/Library/Frameworks/Python.framework/Versions/3.4/bin:${PATH}"
export PATH

# Setting PATH for Python 3.5
# The orginal version is saved in .bash_profile.pysave
PATH="/Library/Frameworks/Python.framework/Versions/3.5/bin:${PATH}"
export PATH

# added by Anaconda3 2.4.1 installer
export PATH="/Users/John/anaconda/bin:$PATH"

# Setting PATH for Python 2.7
# The orginal version is saved in .bash_profile.pysave
PATH="/Library/Frameworks/Python.framework/Versions/2.7/bin:${PATH}"
export PATH

# Aliases
alias blender=/Applications/blender.app/Contents/MacOS/blender
alias desktop='cd ~/desktop'
alias bcoelc='ssh coelc@gauss.engr.ucr.edu'
alias output='tee ~/Desktop/terminalOut.txt'
alias gh='cd /Users/John/GitHub'
alias download='wget -r --no-parent'

##
# Your previous /Users/John/.bash_profile file was backed up as /Users/John/.bash_profile.macports-saved_2016-09-02_at_21:31:54
##

# MacPorts Installer addition on 2016-09-02_at_21:31:54: adding an appropriate PATH variable for use with MacPorts.
export PATH="/opt/local/bin:/opt/local/sbin:$PATH"
# Finished adapting your PATH environment variable for use with MacPorts.

