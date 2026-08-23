.PHONY: update

update:
ifndef MSG
	$(error MSG is not set. Usage: make update MSG="your commit message")
endif
	git add .
	git commit -m "$(MSG)"
	git push
