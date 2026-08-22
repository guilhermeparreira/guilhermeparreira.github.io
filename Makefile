.PHONY: update

update: # Github io builds the website
	git add .
	git commit -m "website with docker and tags reviewed"
	git push
