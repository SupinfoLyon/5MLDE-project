import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HeroTextComponent } from './hero-text.component';

describe('HeroTextComponent', () => {
  let component: HeroTextComponent;
  let fixture: ComponentFixture<HeroTextComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ HeroTextComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HeroTextComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
