<a id="readme-top"></a>


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/caizencloud/caizen">
    <img src="img/psychiac-logo.png" alt="Logo" width="160" height="160">
  </a>

  <h3 align="center">Psychiac</h3>

  <p align="center">
    Capture Terraform changes in CI before apply and send them to <a href="https://github.com/caizencloud/caizen">CAIZEN</a> for "what-if" attack-path analysis.
    <br />
    <br />
    <a href="https://youtu.be/Bltr5Bn2-70">View fwd:cloudsec 2024 Talk</a>
    ·
    <a href="https://docs.google.com/presentation/d/1TotkfJIeCdl8ftN4i4OlQnZA5Hs4K-03EQoSYbWwdBc">View Talk Slides</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This is a _**proof-of-concept**_ tool that runs in your CI pipeline after the Terraform "plan" but before "apply". It works by intercepting Terraform provider calls as they communicate with the Cloud Service Provider APIs to capture a high-fidelity proposed "changeset". It then leverages [CAIZEN](https://github.com/caizencloud/caizen) to perform "what-if?" analysis on that changeset by showing attack paths that will be newly created, kept as-is, or removed to be able to inform the pipeline of the future state if the change were to go through.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [MitmProxy](https://mitmproxy.org/) - A swiss-army knife for debugging, testing, privacy measurements, and penetration testing. It can be used to intercept, inspect, modify and replay web traffic.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps.


### Installation

1. Install [mitmproxy](https://mitmproxy.org/)
2. Install python 3.11+
3. Install [Terraform](https://developer.hashicorp.com/terraform/install)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

This project is currently only runnable in a demo-like fashion to showcase the potential value and is not yet fit for general use. See the [talk](https://youtu.be/Bltr5Bn2-70) for how it could be used.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Proof of value
- [ ] Support for additional resources

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- LICENSE -->
## License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

This project is not quite ready to accept external contributions.  In the meantime, feel free to contact me about your specific needs.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Brad Geesaman - [@bradgeesaman](https://twitter.com/bradgeesaman)

Project Link: [https://github.com/caizencloud/caizen](https://github.com/caizencloud/caizen)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Here are a list of related resources:

* [CAIZEN](https://github.com/caizencloud/caizen) - Harness the security superpowers of your GCP Cloud Asset Inventory.
* [Terraform](https://www.terraform.io/) - Infrastructure automation to provision and manage resources in any cloud or data center.
* [MitM Addons](https://docs.mitmproxy.org/stable/addons-overview/) - Addons interact with mitmproxy by responding to events, which allow hooking into and changing the behavior of how traffic is handled.
* [Google Cloud Asset Inventory](https://cloud.google.com/asset-inventory/docs/overview) - A full cloud resource inventory service.
* [MITRE ATT&CK® Framework](https://attack.mitre.org/) - A security framework for modeling attacker behaviors.
* [OpenCSPM](https://github.com/OpenCSPM/opencspm) - Prior work in this space using Ruby and RedisGraph with my coworker [joshlarsen](https://github.com/joshlarsen)
* [Cartography](https://github.com/lyft/cartography) - Original inspiration for OpenCSPM and now CAIZEN came from Cartography by Lyft. Cartography consolidates infrastructure assets and the relationships between them in an intuitive graph view.

<p align="right">(<a href="#readme-top">back to top</a>)</p>