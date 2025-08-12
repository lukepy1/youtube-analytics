IMAGE_NAME := youtube-ingest
AWS_REGION := us-east-1
ACCOUNT_ID := $(shell aws sts get-caller-identity --query Account --output text)
REPO_URI := $(ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(IMAGE_NAME)
TAG := latest


.PHONY: all login build tag push deploy

all: login build tag push

login:
	@aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(REPO_URI)

build:
	docker build --provenance false -t $(IMAGE_NAME) ./ingest

tag:
	docker tag $(IMAGE_NAME):latest $(REPO_URI):$(TAG)

push:
	docker push $(REPO_URI):$(TAG)

deploy: all
