import adsk.core, adsk.fusion, adsk.cam, traceback, math, random

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('SampleScriptButtonId', 
                                                   'Python Sample Button', 
                                                   'Sample button tooltip')
        
        # Connect to the command created event.
        sampleCommandCreated = SampleCommandCreatedEventHandler()
        buttonSample.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)
        
        # Execute the command.
        buttonSample.execute()
        
        # Keep the script running.
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class SampleCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            app = adsk.core.Application.get()
            ui = app.userInterface
            cmd = args.command
            inputs = cmd.commandInputs
            
            width = inputs.addValueInput('_width', 'Width', 'cm', adsk.core.ValueInput.createByReal(100))
            height = inputs.addValueInput('_height', 'Height', 'cm', adsk.core.ValueInput.createByReal(70))
            circleNumber = inputs.addValueInput('_circleNumber', 'The number of circles', '', adsk.core.ValueInput.createByReal(500))
            offset = inputs.addValueInput('_offset', 'Distance between circles', 'cm', adsk.core.ValueInput.createByReal(0.2))
            maxTries = inputs.addValueInput('_maxTries', 'Max number of tries', '', adsk.core.ValueInput.createByReal(1000))
            radius = inputs.addValueInput('_radius', 'Max radius of the circle', 'cm', adsk.core.ValueInput.createByReal(4))
            valC = inputs.addValueInput('_valC', 'Coefficient', '', adsk.core.ValueInput.createByReal(0.0008))
            
    
            # Connect to the execute event.
            onExecute = SampleCommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
        
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the execute event.
class SampleCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        app = adsk.core.Application.get()
        ui = app.userInterface
        try:
            cmd = args.firingEvent.sender
            
            
            width = cmd.commandInputs.itemById('_width')
            height = cmd.commandInputs.itemById('_height')
            circleNumber = cmd.commandInputs.itemById('_circleNumber')
            offset = cmd.commandInputs.itemById('_offset')
            maxTries = cmd.commandInputs.itemById('_maxTries')
            radius = cmd.commandInputs.itemById('_radius')
            valC = cmd.commandInputs.itemById('_valC')
            
            design = app.activeProduct
            # Get the root component of the active design.
            rootComp = design.rootComponent
            
             # Create a new sketch on the xy plane.
            sketches = rootComp.sketches
            xyPlane = rootComp.xYConstructionPlane
            sketch = sketches.add(xyPlane)
            
            figures = []
    
            #create point for rectangular surface
            point1 = adsk.core.Point3D.create(0,0,0)
            point2 = adsk.core.Point3D.create(width,0,0)
            point3 = adsk.core.Point3D.create(width,height,0)
            point4 = adsk.core.Point3D.create(0,height,0)
    
            #connect point with lines
            sketch.sketchCurves.sketchLines.addByTwoPoints(point1, point2)
            sketch.sketchCurves.sketchLines.addByTwoPoints(point2, point3)
            sketch.sketchCurves.sketchLines.addByTwoPoints(point3, point4)
            sketch.sketchCurves.sketchLines.addByTwoPoints(point4, point1)
            
            def separated(arr, point, offset):
                x1 = point[0]
                y1 = point[1]
                r1 = point[2]
                for i in range (len(arr)):
                    x = arr[i][0]
                    y = arr[i][1]
                    r = arr[i][2]
                    dx = x - x1
                    dy = y - y1
                    dr = math.sqrt(dx*dx + dy*dy)
                    if dr < r+r1+offset:
                        return False
                return True
                
            x = round(random.uniform(radius + offset, width - radius - offset), 2)
            y = round(random.uniform(radius + offset, height - radius - offset), 2)
            r = radius
            figures.append([x,y,r])
            
            for i in range(circleNumber):
                i += 1
                new_rad = r * (1/i**(valC))
                is_pushed = False
                tries = 0
                while (not is_pushed) and (tries < maxTries):
                    tries += 1
                    x = round(random.uniform(new_rad + offset, width - new_rad - offset), 2)
                    y = round(random.uniform(new_rad + offset, height - new_rad - offset), 2)
                    r = new_rad
                    point = [x,y,r]
                    if separated(figures, point, offset):
                        figures.append(point)
                        is_pushed = True
                        tries = 0
            
            #draw
            for i in range(len(figures)):
                x = figures[i][0]
                y = figures[i][1]
                r = figures[i][2]
                #print((x,y))
                p = adsk.core.Point3D.create(x, y, 0)
                sketch.sketchCurves.sketchCircles.addByCenterRadius(p, r)
                
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
        
           
def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Delete the command definition.
        cmdDef = ui.commandDefinitions.itemById('SampleScriptButtonId')
        if cmdDef:
            cmdDef.deleteMe()            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))