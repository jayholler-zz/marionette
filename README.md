# Marionette
An exercise for a job interview at Slack

# Goals
You will be given the IP addresses and <code>root</code> passwords for two newly-provisioned servers running Ubuntu Linux. These are the application and database layer of a hypothetical new startup called Hello World and it is your job to configure them for production service. You may assume a few things:

* The application speaks the HTTP protocol and so should be available on port 80.
* There will be a highly-available load balancer between the Internet and these servers.
* In a real production situation, Hello World doesn't login as root and doesn't use passwords for SSH but in this case please **do not** set <code>PasswordAuthentication no</code> or <code>PermitRootLogin no</code> in <code>/etc/ssh/sshd_config</code>.
* Hello World will need to provision lots of these so repeatability is important.

**You may not use modern configuration management tools like Puppet, Chef, CFEngine, Ansible, Salt, Fabric, etc. Instead, please construct a primitive configuration management system using the programming language(s) of your choice and use it to configure these servers. Consider the features of off-the-shelf tools a production-ready solution to this problem demands.**

The job is done when both servers are responding <code>200 OK</code> with the content <code>Hello, world!\n</code> to requests to <code>GET /</code> requests made via <code>curl -sv "http://ADDRESS"</code>.

Here is Hello World's source code, <code>index.php</code>:<br>
<code><?php</code><br>
<code>header("Content-Type: text/plain");</code><br>
<code>echo "Hello, world!\n";</code><br>
