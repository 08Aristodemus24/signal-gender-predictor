variable "project_name" {
  default = "sgppipeline"
}

variable "containers" {
  type    = list(string)
  default = ["bronze", "silver", "gold", "miscellaneous"]
}