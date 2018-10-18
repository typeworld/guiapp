import os


lines = []
lines.append('[Files]')


rootdir = "Z:\\Code\\TypeWorldApp\\Windows\\Main"

for subdir, dirs, files in os.walk(rootdir):
	for file in files:

		if not file.startswith('.'):

			path = os.path.join(subdir, file)
			lines.append('"%s" "%s"' % (path, path[len(rootdir) + 1:]))


f = open(os.path.join(os.path.dirname(__file__), 'mapping.txt'), 'w')
f.write('\n'.join(lines))
f.close()