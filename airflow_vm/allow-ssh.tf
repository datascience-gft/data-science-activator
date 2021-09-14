resource "google_compute_firewall" "shared-network-allow-ssh" {
  name = "shared-network-allow-ssh"
  network       = var.standard_network
  #network = google_compute_network.shared_network.name
  # enable_logging = false
  priority    = "65534"
  direction   = "INGRESS"
  disabled    = false
  source_ranges = ["0.0.0.0/0"]

  allow {
    protocol = "tcp"
    ports = ["22"]
  }
}
