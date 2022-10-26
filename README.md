# README

Microhubs-controller is an application that controls the opening and closing of microhubs, this data is shared with operators of shared mobility via MDS /stops

# How to deploy?

Build api with:

1. `docker build -t registry.gitlab.com/bikedashboard/microhubs-controller:<version_number> .` (see kubernetes deployment or https://gitlab.com/bikedashboard/dashboard-api/container_registry/387535 for the previous version, or run `kubectl edit deployment microhubs-controller` and check `template.spec.image`).

2. `docker push registry.gitlab.com/bikedashboard/microhubs-controller:<version_number>` (make sure you are logged in to gitlab registry)

3. edit deployement with `kubectl edit deployment microhubs-controller` replace version_number with the new version number.

In example:

    docker build -t registry.gitlab.com/bikedashboard/microhubs-controller:1.3.0 .

    docker push registry.gitlab.com/bikedashboard/microhubs-controller:1.3.0

    kubectl edit deployment microhubs-controller # And change version to 1.3.0
