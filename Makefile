NATIVES = $(shell find . -name Android.mk)
SOURCES = $(shell find . -name *.java)

DX = /drozer/src/drozer/lib/dx
JAVAC = javac
NDKBUILD = ndk-build
PYTHON = python

SDK = /drozer/src/drozer/lib/android.jar

apks: $(SOURCES:.java=.apk)
clean:
	rm -f $(SOURCES:.java=.class) $(SOURCES:.java=.apk)
native-libraries: $(NATIVES)

%.apk: %.class
	cd $(dir $^); $(DX) --dex --output=$(notdir $(^:.class=.apk) $(^:.class=*.class))
%.class: %.java
	cd $(dir $^); $(JAVAC) -cp $(SDK) $(notdir $^)
%.mk: force
	cd $(dir $@); $(NDKBUILD)

force: ;
