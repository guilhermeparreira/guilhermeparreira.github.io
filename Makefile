.PHONY: update

update: # Github io builds the website
	git add .
	git commit -m "new website version"
	git push
