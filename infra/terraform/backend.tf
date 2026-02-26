terraform {
  cloud {

    organization = "myorgisivar"

    workspaces {
      name = "simple-app"
    }
  }
}
